from __future__ import annotations


from lib.deploy import readiness


def test_deploy_readiness_reports_static_viewer_and_masks_env(tmp_path, monkeypatch):
    output_root = tmp_path / "output"
    viewer = output_root / "demo"
    viewer.mkdir(parents=True)
    (viewer / "viewer.html").write_text("<html></html>", encoding="utf-8")
    monkeypatch.setenv("PORTAL_USERNAME", "team")
    monkeypatch.setenv("PORTAL_PASSWORD", "secret-password")
    monkeypatch.setenv("OPENAI_API_KEY", "secret-openai")
    monkeypatch.setattr(readiness.shutil, "which", lambda name: "/usr/local/bin/vercel")

    payload = readiness.check_deploy_readiness(
        output_root=output_root,
        project="demo",
        public=True,
    )

    checks = {check["key"]: check for check in payload["checks"]}
    assert payload["ok"] is True
    assert checks["static_viewer"]["ok"] is True
    assert checks["vercel_cli"]["ok"] is True
    assert checks["portal_auth"]["ok"] is True
    assert checks["openai_key"]["ok"] is True
    assert "secret" not in str(payload)


def test_deploy_readiness_does_not_require_provider_keys_for_static_review(tmp_path, monkeypatch):
    output_root = tmp_path / "output"
    output_root.mkdir()
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setattr(readiness.shutil, "which", lambda name: None)

    payload = readiness.check_deploy_readiness(output_root=output_root)

    checks = {check["key"]: check for check in payload["checks"]}
    assert payload["ok"] is False
    assert checks["gemini_key"]["required"] is False
    assert checks["openai_key"]["required"] is False
