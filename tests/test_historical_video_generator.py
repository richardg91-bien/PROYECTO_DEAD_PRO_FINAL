from app.historical_video.generator import HistoricalSource, crear_video_historico


def test_crear_video_historico_preserves_sources():
    plan = crear_video_historico(
        subject="Rómulo y Remo",
        narration="La tradición romana cuenta la historia de dos hermanos. Fueron asociados con el origen legendario de Roma.",
        sources=[HistoricalSource("Tito Livio", "Ab Urbe Condita", "tradición literaria")],
        target_duration_seconds=60,
    )

    assert plan.title == "Historia de Rómulo y Remo"
    assert len(plan.scenes) == 2
    assert "Tito Livio" in plan.scenes[0].source_notes[0]
    assert "Ab Urbe Condita" in plan.scenes[0].source_notes[0]
