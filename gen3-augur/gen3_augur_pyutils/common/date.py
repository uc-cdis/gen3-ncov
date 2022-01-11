"""Format date utilities
@author: Yilin Xu <yilinxu@uchicago.edu>
"""

from datetime import datetime


def date_conform(date_string):
    try:
        date = datetime.strptime(date_string, "%d-%b-%Y")
    except:
        try:
            date = datetime.strptime(date_string, "%Y-%m-%d")
        except:
            try:
                date = datetime.strptime(date_string, "%Y-%m")
            except:
                try:
                    date = datetime.strptime(date_string, "%b-%Y")
                except:
                    date = datetime.strptime(date_string, "%Y")
    finally:
        return date.date()
