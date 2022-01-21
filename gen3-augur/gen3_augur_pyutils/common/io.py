"""IO common utilities
@author: Yilin Xu <yilinxu@uchicago.edu>
"""

import json
from contextlib import contextmanager
from os import walk, path, chdir, getcwd
from pathlib import Path
from typing import List, Dict

import pandas as pd
import re

from gen3_augur_pyutils.common.types import DataFrameT


class IO(object):
    @staticmethod
    def gather_file(dir: object) -> object:
        """
        :param dir: path of the directory
        :return: files path under the directory
        """
        for (dirpath, dirnames, filenames) in walk(dir):
            for item in filenames:
                yield path.join(dirpath, item)

    @staticmethod
    def parse_json(file: str) -> DataFrameT:
        """
        Extract key value pairs in json file
        :param file: file path
        :return: DataFrame key value pairs from json file
        """
        fh = open(file, "r")
        items = json.load(fh)
        fh.close()
        items_df = pd.DataFrame(items)
        return items_df

    @staticmethod
    def df_merge_columns(file: str, columns: List) -> DataFrameT:
        """
        Parse csv file and merge columns
        :param file:
        :return: DataFrameT
        """
        df = pd.read_csv(file, header=True)
        df["combine"] = df[columns].apply(lambda x: ",".join(x), axis=1)
        return df

    @staticmethod
    def write_file(file: str, content: List) -> None:
        """
        Write content into a file
        :param file: output file path
        :param content:
        :return:
        """
        fh = open(file, "w")
        fh.writelines("%s" % item for item in content)
        fh.close()

    @staticmethod
    def write_json(file: str, data: Dict) -> None:
        """
        Write content into a file
        :param file: output file path
        :param data: data to write
        :return:
        """
        jstr = json.dumps(data, ensure_ascii=False, indent=4)
        with open(file, "w") as outfile:
            outfile.write(jstr)

    def rm_bk_qt(file: str, file_format: str) -> None:
        """
        Remove sqaure bracket and quote in csv file
        :param file: file path
        :return:
        """
        ifh = open(file, "r")
        lines = ifh.readlines()
        ifh.close()
        ofh = open(file, "w")
        for line in lines:
            line = re.sub(r"[\'\[\]]", "", line)
            ofh.write(line)
        ofh.close()
        if file_format == "csv":
            df = pd.read_csv(file)
            df.to_csv(file, date_format="%Y-%m-%d", header=True, index=False)
        elif file_format == "tsv":
            df = pd.read_csv(file, sep="\t")
            df.to_csv(file, date_format="%Y-%m-%d", header=True, index=False, sep="\t")

    @staticmethod
    def abs_path(level: int, file_path: str) -> str:
        """
        Absolute path relative to the current file
        : param level: level of parent
        : param path: path relative to the common parent with the current file
        : return: absolute path
        """
        dir_path = Path(__file__).resolve().parents[level]
        abs_path = path.join(dir_path, file_path)
        return abs_path

    @staticmethod
    @contextmanager
    def change_dir(destination):
        """
        Change to destination to do task and change back to the original directory
        :param destination: Target path performing a task
        :return: None
        """
        try:
            cwd = getcwd()
            chdir(destination)
            yield
        finally:
            chdir(cwd)
