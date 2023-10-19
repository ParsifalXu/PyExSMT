def _check_solver(solver, penalty, dual):
    # TODO(1.4): Remove "none" option
    if solver not in ["liblinear", "saga"] and penalty not in ("l2", "none", None):
        raise ValueError(
            "Solver %s supports only 'l2' or 'none' penalties, got %s penalty."
            % (solver, penalty)
        )
    if solver != "liblinear" and dual:
        raise ValueError(
            "Solver %s supports only dual=False, got dual=%s" % (solver, dual)
        )

    if penalty == "elasticnet" and solver != "saga":
        raise ValueError(
            "Only 'saga' solver supports elasticnet penalty, got solver={}.".format(
                solver
            )
        )

    if solver == "liblinear" and penalty == "none":
        raise ValueError("penalty='none' is not supported for the liblinear solver")

    return solver