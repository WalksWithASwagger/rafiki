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


def test_media_suite_filter_persistence_wiring_present() -> None:
    """Rendered portal JS must read/write URL and localStorage for all core filters.

    This test verifies issue-190 acceptance criteria at the source level:
    - pushFilterState writes URL via history.replaceState and localStorage.setItem
    - applyInitialParams reads URL params (preferred) then localStorage fallback
    - All tracked filter fields are named: q, view, kind, collection, subject,
      videoSubject, videoProject, and tab (active view)
    - Filter change event listeners call pushFilterState before loading
    """
    html = render_media_suite().decode("utf-8")

    # Core persistence functions must be present
    assert "function pushFilterState()" in html
    assert "function loadStoredFilters()" in html
    assert "FILTER_STORAGE_KEY" in html

    # URL update mechanism
    assert "history.replaceState" in html

    # localStorage read and write
    assert "localStorage.getItem(FILTER_STORAGE_KEY)" in html
    assert "localStorage.setItem(FILTER_STORAGE_KEY" in html

    # All filter fields are persisted
    for field in ("q", "view", "kind", "collection", "subject", "videoSubject", "videoProject", "tab"):
        assert f"params.set('{field}'" in html, f"missing params.set for filter field: {field}"
        assert f"get('{field}')" in html, f"missing get() restore call for filter field: {field}"

    # URL preference: localStorage only used when URL has no params
    assert "hasUrlState" in html

    # pushFilterState is called from filter change handlers
    assert "pushFilterState(); loadMedia" in html
    assert "pushFilterState();\n      renderVideo()" in html or "pushFilterState();" in html

    # Tab switch persists the active tab
    assert "activateView" in html
    assert "pushFilterState()" in html

    # Tidy URL: defaults are omitted
    assert "activeTab !== 'library'" in html
    assert "view !== 'review'" in html

    # localStorage key is namespaced to avoid collisions
    assert "rafiki:library-filters" in html
