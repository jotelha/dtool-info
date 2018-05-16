"""Test the report command."""

from click.testing import CliRunner

from . import REPORT_DATASETS_DIR


def test_report_functional():

    from dtool_info.report import report

    runner = CliRunner()
    result = runner.invoke(report, [REPORT_DATASETS_DIR])
    assert result.exit_code == 0

    expected = [
        "19.0B   olssont 3 2018-05-16 big_cats",
        "11.0B   olssont 2 2018-05-16 toys",
        "30.0B           5"
    ]
    actual = result.output.strip().split("\n")
    for e, a in zip(expected, actual):
        assert e.strip() == a.strip()


def test_report_html_functional():

    from dtool_info.report import report

    runner = CliRunner()
    result = runner.invoke(report, ["-f", "html", REPORT_DATASETS_DIR])
    assert result.exit_code == 0

    assert result.output.find("<html>") != -1
    assert result.output.find("</html>") != -1


def test_report_csv_functional():

    from dtool_info.report import report

    runner = CliRunner()
    result = runner.invoke(report, ["-f", "csv", REPORT_DATASETS_DIR])
    assert result.exit_code == 0

    expected_starts = [
        "name,size_in_bytes,creator,num_items,date,uri",
        "big_cats,19,olssont,3,2018-05-16",
        "toys,11,olssont,2,2018-05-16",
    ]
    for a, e in zip(result.output.split("\n"), expected_starts):
        assert a.startswith(e)
