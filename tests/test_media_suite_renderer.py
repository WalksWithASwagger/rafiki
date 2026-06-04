from __future__ import annotations

from lib.renderers.media_suite import render_media_suite


def test_media_suite_renders_subject_profile_controls() -> None:
    html = render_media_suite().decode("utf-8")

    assert 'id="subjectCards" class="grid subject-grid"' in html
    assert 'id="subject"' in html
    assert 'id="videoSubject"' in html
    assert "function subjectCardHtml(subject)" in html
    assert "data-library-subject" in html
    assert "data-video-subject" in html
    assert "data-video-project" in html
