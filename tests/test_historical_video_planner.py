from app.historical_video.planner import crear_plan_video


def test_crear_plan_divides_narration_without_inventing_content():
    plan = crear_plan_video(
        "Roma antigua",
        "Primer episodio",
        "Roma crecio junto al Tiber. La ciudad se convirtio en una potencia regional.",
        source_notes=["fuente-1"],
    )

    assert len(plan.scenes) == 2
    assert plan.scenes[0].narration == "Roma crecio junto al Tiber."
    assert plan.scenes[1].narration == "La ciudad se convirtio en una potencia regional."
    assert plan.scenes[0].source_notes == ["fuente-1"]
    assert plan.scenes[0].duration_hint > 0
    assert "Roma crecio junto al Tiber." in plan.scenes[0].visual_prompt
