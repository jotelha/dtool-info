"""Logic for generating reports on collections of datasets."""

import datetime
from operator import itemgetter

import click

from jinja2 import Environment, PackageLoader

import dtoolcore

from dtool_cli.cli import CONFIG_PATH

JINJA2_ENV = Environment(loader=PackageLoader('dtool_info', 'templates'))


def _sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "{:6.1f}{:3s}".format(num, unit + suffix)
        num /= 1024.0
    return "{:6.1f}{:3s}".format(num, "Yi" + suffix)


def _date_fmt(timestamp):
    timestamp = float(timestamp)
    datetime_obj = datetime.datetime.fromtimestamp(timestamp)
    return datetime_obj.strftime("%Y-%m-%d")


def _dataset_info(dataset):
    """Return information about dataset as a dict."""
    info = {}

    info["uri"] = dataset.uri
    info["uuid"] = dataset.uuid

    # Computer and human readable size of dataset.
    tot_size = sum([dataset.item_properties(i)["size_in_bytes"]
                    for i in dataset.identifiers])
    info["size_int"] = tot_size
    info["size_str"] = _sizeof_fmt(tot_size)

    info["creator"] = dataset._admin_metadata["creator_username"]
    info["name"] = dataset._admin_metadata["name"]

    info["date"] = _date_fmt(dataset._admin_metadata["frozen_at"])

    info["num_items"] = len(dataset.identifiers)

    info["readme_content"] = dataset.get_readme_content()

    return info


def _is_frozen_dataset(uri, CONFIG_PATH):
    admin_metadata = dtoolcore._admin_metadata_from_uri(uri, CONFIG_PATH)
    return admin_metadata["type"] == "dataset"


def _base_uri_info(base_uri):
    StorageBroker = dtoolcore._get_storage_broker(base_uri, CONFIG_PATH)

    info = {}
    info["total_size_int"] = 0
    info["total_items"] = 0
    info["datasets"] = []

    for uri in StorageBroker.list_dataset_uris(base_uri, CONFIG_PATH):
        if not _is_frozen_dataset(uri, CONFIG_PATH):
            continue
        dataset = dtoolcore.DataSet.from_uri(uri)
        dataset_info = _dataset_info(dataset)
        info["datasets"].append(dataset_info)
        info["total_size_int"] += dataset_info["size_int"]
        info["total_items"] += dataset_info["num_items"]

    info["total_size_str"] = _sizeof_fmt(info["total_size_int"])
    info["num_datasets"] = len(info["datasets"])

    return info


def _line_formats(info):
    creator_max_len = max(
        [len(ds["creator"]) for ds in info["datasets"]]
    )
    num_items_max_len = max(
        [len(str(ds["num_items"])) for ds in info["datasets"]]
    )

    ds_words = [
        "{size_str}",
        "{" + "creator:{}".format(creator_max_len) + "}",
        "{" + "num_items:{}".format(num_items_max_len) + "}",
        "{date}",
        "{name}",
    ]

    ds_line_format = " ".join(ds_words)

    total_items_offset = creator_max_len + num_items_max_len + 1
    summary_words = [
        "{total_size_str}",
        "{" + "total_items:{}".format(total_items_offset) + "}",
    ]
    summary_line_format = " ".join(summary_words)
    return ds_line_format, summary_line_format


def _cmd_line_report(info):
    # Report on each individual dataset.
    ds_line, summary_line = _line_formats(info)
    for ds_info in sorted(
        info["datasets"],
        key=itemgetter("creator", "date", "name")
    ):
        click.secho(ds_line.format(**ds_info))

    # Summary report on all datasets in base_uri.
    click.secho(summary_line.format(**info))


def _html_report(info):

    template = JINJA2_ENV.get_template("dtool_report.html.j2")
    html = template.render(info)
    click.secho(html)


@click.command()
@click.argument("uri")
@click.option(
    "-f",
    "--format",
    type=click.Choice(["html"]),
    help="Select the output format."
)
def report(uri, format):
    """Generate a report on datasets in a base URI."""
    base_uri = dtoolcore.utils.sanitise_uri(uri)
    info = _base_uri_info(base_uri)

    if format is None:
        _cmd_line_report(info)
    elif format == "html":
        _html_report(info)