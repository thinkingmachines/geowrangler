import nox


@nox.session(python=["3.7", "3.8", "3.9", "3.10"])
def tests(session):
    session.install("pytest")
    session.install("pytest-cov")
    session.install("pytest-xdist")
    session.install("pytest-mock")
    session.run(
        "pip",
        "install",
        "-e",
        ".",
    )

    session.run(
        "pytest",
        "--cov",
        "--cov-config=.coveragerc",
        "--cov-fail-under=80",
        "-n",
        "auto",
    )
