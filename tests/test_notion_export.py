"""Tests for the Notion exporter — fully mocked, no real API calls.

We patch:
  * ``lib.exporters.notion._get_client`` — replaces the notion-client SDK
    so the package does not need to be installed for these tests.
  * ``lib.exporters.notion._upload_file`` — replaces the 3-step REST upload
    flow so we don't hit the network and don't need a real API key.

Tests use ``unittest.TestCase`` so they run under both ``pytest`` and
``python -m unittest``.
"""

from __future__ import annotations

import json
import struct
import sys
import unittest
import zlib
from pathlib import Path
from unittest.mock import MagicMock, patch

# Allow ``lib.exporters.notion`` import without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.exporters import notion as notion_export  # noqa: E402


def _write_png(path: Path) -> None:
    """Write a 1x1 transparent PNG (real bytes — Notion would accept it)."""
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    ihdr_chunk = (
        struct.pack(">I", len(ihdr))
        + b"IHDR" + ihdr
        + struct.pack(">I", zlib.crc32(b"IHDR" + ihdr))
    )
    raw = b"\x00\x00\x00\x00\x00"
    idat = zlib.compress(raw)
    idat_chunk = (
        struct.pack(">I", len(idat))
        + b"IDAT" + idat
        + struct.pack(">I", zlib.crc32(b"IDAT" + idat))
    )
    iend_chunk = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", zlib.crc32(b"IEND"))
    path.write_bytes(sig + ihdr_chunk + idat_chunk + iend_chunk)


class NotionExportTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

        self.output_root = Path(self._tmp.name) / "output"
        self.project = "test-project"
        self.project_dir = self.output_root / self.project
        self.approved_dir = self.project_dir / "approved"
        self.approved_dir.mkdir(parents=True)

        self.img_a = self.approved_dir / "01-week-03-hello.png"
        self.img_b = self.approved_dir / "02-week-03-world.png"
        _write_png(self.img_a)
        _write_png(self.img_b)

        (self.approved_dir / "index.json").write_text(json.dumps({
            "images": [
                {"file": self.img_a.name, "name": "Hello",
                 "caption": "First image", "week": "Week 3"},
                {"file": self.img_b.name, "name": "World",
                 "caption": "Second image"},
            ],
        }), encoding="utf-8")

    # ── helpers ──────────────────────────────────────────────────────────

    def _run(self, **kw):
        defaults = dict(
            project=self.project,
            database_id="db-123",
            output_root=self.output_root,
            api_key="secret_test",
        )
        defaults.update(kw)
        return notion_export.export(**defaults)

    # ── tests ────────────────────────────────────────────────────────────

    def test_export_uploads_each_approved_image(self):
        mock_client = MagicMock()
        mock_client.pages.create.return_value = {"id": "page-x"}

        with patch.object(notion_export, "_get_client", return_value=mock_client) as gc, \
             patch.object(notion_export, "_upload_file",
                          side_effect=["upload-1", "upload-2"]) as up:
            result = self._run()

        gc.assert_called_once_with("secret_test")
        self.assertEqual(up.call_count, 2)
        self.assertEqual(mock_client.pages.create.call_count, 2)
        self.assertEqual(result["exported"], 2)
        self.assertEqual(result["skipped"], 0)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["source"], "approved")

        first = mock_client.pages.create.call_args_list[0].kwargs
        self.assertEqual(first["parent"], {"database_id": "db-123"})
        props = first["properties"]
        self.assertEqual(
            props["Name"]["title"][0]["text"]["content"], "Hello"
        )
        self.assertEqual(
            props["Caption"]["rich_text"][0]["text"]["content"], "First image"
        )
        self.assertEqual(props["Week"]["select"]["name"], "Week 3")
        self.assertEqual(
            props["Image"]["files"][0]["file_upload"]["id"], "upload-1"
        )

    def test_dry_run_does_not_call_notion(self):
        with patch.object(notion_export, "_get_client") as gc, \
             patch.object(notion_export, "_upload_file") as up:
            result = notion_export.export(
                self.project,
                database_id="db-123",
                output_root=self.output_root,
                dry_run=True,
            )
        gc.assert_not_called()
        up.assert_not_called()
        self.assertEqual(result["exported"], 2)
        self.assertTrue(result["dry_run"])

    def test_idempotent_skip_already_exported(self):
        mock_client = MagicMock()
        with patch.object(notion_export, "_get_client", return_value=mock_client), \
             patch.object(notion_export, "_upload_file",
                          side_effect=["u1", "u2", "u3", "u4"]):
            first = self._run()
            second = self._run()

        self.assertEqual(first["exported"], 2)
        self.assertEqual(second["exported"], 0)
        self.assertEqual(second["skipped"], 2)
        # Only the first run created pages
        self.assertEqual(mock_client.pages.create.call_count, 2)

        log = json.loads((self.project_dir / ".notion-exported.json").read_text())
        self.assertIn("db-123", log)
        self.assertEqual(set(log["db-123"].keys()),
                         {self.img_a.name, self.img_b.name})

    def test_force_flag_re_exports(self):
        mock_client = MagicMock()
        with patch.object(notion_export, "_get_client", return_value=mock_client), \
             patch.object(notion_export, "_upload_file",
                          side_effect=["u1", "u2", "u3", "u4"]):
            self._run()
            second = self._run(force=True)

        self.assertEqual(second["exported"], 2)
        self.assertEqual(second["skipped"], 0)
        self.assertEqual(mock_client.pages.create.call_count, 4)

    def test_missing_api_key_raises_clear_error(self):
        with patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop("NOTION_API_KEY", None)
            os.environ.pop("NOTION_DATABASE_ID", None)
            with self.assertRaises(notion_export.NotionExportError) as cm:
                notion_export.export(
                    self.project,
                    database_id="db-123",
                    output_root=self.output_root,
                )
        self.assertIn("NOTION_API_KEY", str(cm.exception))

    def test_falls_back_to_latest_run_when_no_approved_dir(self):
        # Build a project with run-* dirs and no approved/
        proj = self.output_root / "run-only"
        run_old = proj / "run-20260101-000000"
        run_new = proj / "run-20260202-000000"
        run_old.mkdir(parents=True)
        run_new.mkdir(parents=True)
        img1 = run_new / "01-from-latest.png"
        _write_png(img1)
        (run_new / "run.json").write_text(json.dumps({
            "model": "test",
            "images": [{"file": img1.name, "name": "Latest",
                        "prompt": "a prompt used as caption"}],
        }), encoding="utf-8")

        mock_client = MagicMock()
        with patch.object(notion_export, "_get_client", return_value=mock_client), \
             patch.object(notion_export, "_upload_file", return_value="u1") as up:
            result = notion_export.export(
                "run-only",
                database_id="db-123",
                output_root=self.output_root,
                api_key="secret_test",
            )

        self.assertEqual(result["exported"], 1)
        self.assertEqual(result["source"], run_new.name)
        up.assert_called_once()
        # Caption should fall back to the prompt field
        props = mock_client.pages.create.call_args.kwargs["properties"]
        self.assertEqual(
            props["Caption"]["rich_text"][0]["text"]["content"],
            "a prompt used as caption",
        )


if __name__ == "__main__":
    unittest.main()
