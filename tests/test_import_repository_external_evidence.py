from __future__ import annotations

from pathlib import Path

import pytest

from scripts import import_repository_external_evidence as evidence


def _write_filters(path: Path) -> None:
    path.write_text(
        "Filtre,Valeur\nType de recherche,Web\nDate,27 juil. 2026-9 août 2026\nPage,+/repo/\n",
        encoding="utf-8",
    )


def test_build_payload_normalizes_localized_exports(tmp_path: Path) -> None:
    pages = tmp_path / "Pages.csv"
    pages.write_text(
        "Pages les plus populaires,Clics,Impressions,CTR,Position\n"
        "https://claracle.com/repo/example-tool/,0,12,0%,7.5\n",
        encoding="utf-8",
    )
    links = tmp_path / "gsc-top-linked-pages.csv"
    links.write_text(
        "Page cible,Liens entrants,Sites d&#39;origine\nhttps://claracle.com/,15,3\n",
        encoding="utf-8",
    )
    referrals = tmp_path / "ga4-repo-referrals.csv"
    referrals.write_text(
        "# report\n# 20260727-20260811\n"
        "Landing page + query string,Page referrer,Sessions\n"
        "/repo/example-tool/?campaign=external,https://example.com/,2\n",
        encoding="utf-8",
    )
    filters = tmp_path / "Filtres.csv"
    _write_filters(filters)

    payload = evidence.build_payload(
        pages_path=pages,
        links_path=links,
        referrals_path=referrals,
        filters_path=filters,
        links_window="exported 2026-08-10",
    )

    assert payload["search_analytics"]["/repo/example-tool/"] == {
        "clicks": 0,
        "impressions": 12,
        "position": 7.5,
    }
    assert payload["sampled_link_paths"] == []
    assert payload["first_party_referrals"] == {"/repo/example-tool/": 2}
    assert payload["summary"]["search_impressions"] == 12
    assert payload["sources"]["search_analytics"]["window"] == ("2026-07-27..2026-08-09")
    assert payload["sources"]["first_party_referrals"]["window"] == ("2026-07-27..2026-08-11")


def test_build_payload_accepts_metadata_only_ga4_export(tmp_path: Path) -> None:
    pages = tmp_path / "Pages.csv"
    pages.write_text(
        "Pages les plus populaires,Clics,Impressions,Position\n"
        "https://claracle.com/repo/example-tool/,0,1,7.5\n",
        encoding="utf-8",
    )
    links = tmp_path / "links.csv"
    links.write_text("Page cible\nhttps://claracle.com/\n", encoding="utf-8")
    referrals = tmp_path / "ga4.csv"
    referrals.write_text("# report\n# 20260727-20260811\n", encoding="utf-8")
    filters = tmp_path / "filters.csv"
    _write_filters(filters)

    payload = evidence.build_payload(
        pages_path=pages,
        links_path=links,
        referrals_path=referrals,
        filters_path=filters,
        links_window="exported 2026-08-10",
    )

    assert payload["first_party_referrals"] == {}


def test_build_payload_rejects_missing_search_headers(tmp_path: Path) -> None:
    pages = tmp_path / "Pages.csv"
    pages.write_text("Page,Clicks\n/repo/example/,0\n", encoding="utf-8")
    links = tmp_path / "links.csv"
    links.write_text("Page cible\nhttps://claracle.com/\n", encoding="utf-8")
    referrals = tmp_path / "ga4.csv"
    referrals.write_text("# report\n# 20260727-20260811\n", encoding="utf-8")
    filters = tmp_path / "filters.csv"
    _write_filters(filters)

    with pytest.raises(ValueError, match="impressions header"):
        evidence.build_payload(
            pages_path=pages,
            links_path=links,
            referrals_path=referrals,
            filters_path=filters,
            links_window="exported 2026-08-10",
        )


def test_build_payload_rejects_unscoped_search_export(tmp_path: Path) -> None:
    pages = tmp_path / "Pages.csv"
    pages.write_text(
        "Pages les plus populaires,Clics,Impressions,Position\n"
        "https://claracle.com/repo/example-tool/,0,1,7.5\n",
        encoding="utf-8",
    )
    links = tmp_path / "links.csv"
    links.write_text("Page cible\nhttps://claracle.com/\n", encoding="utf-8")
    referrals = tmp_path / "ga4.csv"
    referrals.write_text("# report\n# 20260727-20260811\n", encoding="utf-8")
    filters = tmp_path / "filters.csv"
    filters.write_text(
        "Filtre,Valeur\nType de recherche,Web\nDate,27 juil. 2026-9 août 2026\nPage,+/weekly/\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="not scoped to /repo/"):
        evidence.build_payload(
            pages_path=pages,
            links_path=links,
            referrals_path=referrals,
            filters_path=filters,
            links_window="exported 2026-08-10",
        )
