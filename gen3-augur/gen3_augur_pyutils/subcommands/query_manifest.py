"""
Query genomic data file and save in json format

@author: Yilin Xu <yilinxu@uchicago.edu>
         Qiong Liu <qiongl@uchicago.edu>
"""

import json
import requests
from datetime import date
from os import path
import os
import re
import sys
import pandas as pd

from gen3_augur_pyutils.common.io import IO
from gen3_augur_pyutils.common.logger import Logger
from gen3_augur_pyutils.common.types import ArgParserT, NamespaceT, LoggerT
from gen3_augur_pyutils.subcommands import Subcommand


class Gen3Query(Subcommand):
    @classmethod
    def __add_arguments__(cls, parser: ArgParserT) -> None:
        """
        Add the arguments to the parser
        :param parser: parsed arguments
        :return: None
        """
        parser.add_argument("--url", required=True, help="data common url")
        parser.add_argument("--type", required=True, help="define type in guppy query")
        parser.add_argument(
            "--fields",
            required=True,
            help="properties to query that separated with comma",
        )
        parser.add_argument(
            "--filter", required=False, help="property name for filtering"
        )
        parser.add_argument(
            "--value", required=False, help="property value for filtering"
        )
        parser.add_argument(
            "--format",
            required=True,
            choices=["json", "csv", "tsv"],
            help="output file format",
        )
        parser.add_argument("--logfile", required=True, help="log file name")

    @classmethod
    def get_token(cls, url: str) -> str:
        """
        Helper function for generating token.
        :params url: data common url to query from
        """
        keyfile = os.getenv("GEN3_API_KEY")
        if not keyfile:
            raise Exception(
                "GEN3_API_KEY environment not set - ex: $HOME/.gen3/credentials.json"
            )
        abs_path = IO.abs_path(2, keyfile)
        with open(abs_path, "r") as f:
            creds = json.load(f)
        token_url = url + "user/credentials/api/access_token"
        token = requests.post(token_url, json=creds).json()["access_token"]
        return token

    @classmethod
    def query_manifest(cls, headers: dict, query_obj: dict, logger: LoggerT) -> dict:
        """
        Query metadata from gen3 data common guppy download endpoint
        :params headers: header for requests which has token
        :params query_obj: dictionary object that has parameters for query
        """
        project = os.getenv("project_id")
        api_url = query_obj["url"] + "guppy/download"
        if query_obj["filter"]:
            query = {
                "type": query_obj["type"],
                "fields": query_obj["fields"],
                "filter": {"=": {query_obj["filter"]: query_obj["value"]}},
            }
        else:
            query = {"type": query_obj["type"], "fields": query_obj["fields"]}

        response = requests.post(api_url, json=query, headers=headers,)
        try:
            data = json.loads(response.text)
            if query_obj["format"] == "json":
                IO.write_json(query_obj["file"], data)
                return len(data)
            else:
                df = pd.DataFrame(data)
                df.drop(
                    [
                        "organism",
                        "file_name",
                        "sample_type",
                        "object_id",
                        "nextstrain_clade",
                        "file_size",
                        "zipcode",
                        "isolate",
                        "md5sum",
                        "isolation_source",
                    ],
                    axis=1,
                    inplace=True,
                )
                df.rename(
                    columns={
                        "collection_date": "date",
                        "submitter_id": "strain",
                        "county": "location",
                        "country_region": "country",
                        "continent": "region",
                        "province_state": "division",
                        "submitting_lab_PI": "authors",
                    },
                    inplace=True,
                )

                # create new series of correct strain names
                strain_name = df["strain"].str.replace(project + "_", "")
                strain_name = strain_name.apply(lambda r: "/".join(r.split("_")[:-1]))

                df = df.apply(lambda x: x.str[0])
                df["strain"] = strain_name

                location_translation_abs_path = IO.abs_path(
                    2, "config/IL_county_translation_table.csv"
                )
                location_translation = pd.read_csv(location_translation_abs_path)

                location_translation_dict = dict(location_translation.values)

                df.replace({"location": location_translation_dict}, inplace=True)

                df.loc[df["region"] == "Asia", "country"] = "China"
                df.loc[df["region"] == "Asia", "division"] = "Hubei"
                df.loc[df["region"] == "Asia", "location"] = "Wuhan"

                df["region_exposure"] = df["region"]
                df["country_exposure"] = df["country"]
                df["division_exposure"] = df["division"]
                df["location_exposure"] = df["location"]
                df["virus"] = "ncov"
                df["segment"] = "genome"
                df.replace(to_replace=r"\?{3}", value="NA", regex=True, inplace=True)

                if query_obj["format"] == "csv":
                    df.to_csv(query_obj["file"], header=True, index=False, na_rep="?")

                elif query_obj["format"] == "tsv":
                    df.to_csv(
                        query_obj["file"],
                        header=True,
                        index=False,
                        sep="\t",
                        na_rep="?",
                    )

                IO.rm_bk_qt(query_obj["file"], query_obj["format"])
                return len(data)
        except requests.exceptions.Timeout:
            logger.error("Error querying Guppy, object data query failed")

    @classmethod
    def main(cls, options: NamespaceT):
        """
        Entrypoint for Gen3Query
        :param options:
        :return:
        """
        rel_path = path.join("logs", options.logfile)
        log_path = IO.abs_path(2, rel_path)
        logger = Logger.get_logger(cls.__tool_name__(), log_path)
        logger.info(cls.__get_description__())

        # Construct object with argument information

        today = date.today()
        day = str(today.strftime("%m%d%y"))
        file_name = options.type + "_" + day + "_manifest." + options.format
        rel_path = path.join("data", file_name)
        file_path = IO.abs_path(2, rel_path)
        fields = options.fields.split(",")
        query_obj = {
            "type": options.type,
            "fields": fields,
            "filter": options.filter,
            "value": options.value,
            "file": file_path,
            "url": options.url,
            "format": options.format,
        }
        # Get token
        token = cls.get_token(query_obj["url"])
        headers = {"Authorization": "bearer " + token}

        # Query metadata from Gen3 data common
        size = cls.query_manifest(headers, query_obj, logger)
        logger.info(f"download manifest files for {size} genomic sequences")
        sys.stdout.write(str(size))
