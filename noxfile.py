import nox


@nox.session(python=["3.7", "3.8", "3.9", "3.10"])
def tests(session):
    session.install("poetry")
    session.run("poetry", "install")
    session.run(
        "poetry",
        "run",
        "pytest",
        "--cov",
        "--cov-config=.coveragerc",
        "--cov-fail-under=80",
        "-n",
        "auto",
    )
