"""Combine dataframe common utilities
@author: Yilin Xu <yilinxu@uchicago.edu>
"""


def merge_multiple_columns(
    left_df, right_df, left_merge_column, right_merge_columns, right_target_column
):
    """
    The to be merged column of first dataframe codes information in multiple ways.
    The second dataframe has multiple columns, each column code the same information in one way.
    This function allows the first dataframe merge on multiple columns from the second dataframe.
    :param left_df: First dataframe
    :param right_df: Second dataframe
    :param left_merge_column: The column name on the first dataframe
    :param right_merge_columns: Multiple columns names on the second dataframe
    :param right_target_column: The additional information from second dataframe to be included in the merged dataframe
    :return:
    """
    for c_name in right_merge_columns:
        left_df = left_df.merge(
            right_df[[c_name, right_target_column]],
            how="left",
            left_on=left_merge_column,
            right_on=c_name,
        ).drop(c_name, axis="columns")
    merge_columns = [x for x in left_df.columns if right_target_column in x]
    left_df[right_target_column] = left_df[merge_columns].apply(
        lambda x: "".join(x.dropna().astype(str)), axis=1
    )
    merge_columns.remove(right_target_column)
    left_df = left_df.drop(columns=merge_columns)
    return left_df
