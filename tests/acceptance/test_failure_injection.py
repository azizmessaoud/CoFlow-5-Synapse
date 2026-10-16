from __future__ import annotations


def test_transport_exception_is_visible_not_silently_swallowed() -> None:
    from coflow5.messaging import MessageDisposition, read_a1_advisories

    class FailingTransport:
        def read(self, *args, **kwargs):
            raise RuntimeError("injected adviser transport failure")

    result = read_a1_advisories(
        FailingTransport(),  # type: ignore[arg-type]
        run_id="visible-failure", scenario_hash="sha256:" + "d" * 64,
        signal_id="J0", valid_at=1.0,
    )
    assert result.disposition is MessageDisposition.UNAVAILABLE
    assert result.advisories == ()
    assert result.transport_error == "RuntimeError: injected adviser transport failure"
