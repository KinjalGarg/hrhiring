import re
import datetime
import locale
from typing import Any
import docx2pdf
from num2words import num2words
import pandas as pd

from docxtpl import DocxTemplate, InlineImage, RichText
from loi_producer_config import *


def get_position_of_a_day(day: int) -> str:
    """
    This function accepts a day(in number) in a month and returns the position of the day

    Args:
        day (int): Day of a month

    Returns:
        str: Position of the day

    Raises:
         ValueError: when the day is not between 0 and 31 inclusive

    Example:
        > Returns 'st' if day is 1, 11, 21 etc.\n
        > Returns 'nd' if day is 2, 12, 22 etc.\n
        > Returns 'st' if day is 3, 13, 23 etc.\n
        > Otherwise, returns 'th'

        >>> get_position_of_a_day(11)
        'st'
        >>> get_position_of_a_day(22)
        'nd'
        >>> get_position_of_a_day(25)
        'th'
    """
    suffix = ""
    try:
        if 1 <= day <= 31:
            if 4 <= day <= 20 or 24 <= day <= 30:
                suffix = "th"
            else:
                suffix = ["st", "nd", "rd"][(day % 10) - 1]
            # return suffix
        else:
            raise ValueError
    except ValueError:
        print("Day is out of range, should be between 1 and 31 inclusive")
    finally:
        return suffix


def configure_rich_text_web_link(
    template: DocxTemplate,
    company_dataframe: pd.DataFrame,
    company_name: str
) -> RichText:
    """
    This function is used for configuring the rich text object for
    embedding the clickable WebSite in the document

    Args:
        template (DocxTemplate): The DocxTemplate object which holds template information
        company_dataframe (pd.DataFrame): The Pandas DataFrame containing company information
        company_name (str): The name of the company

    Returns:
        RichText: The configured RichText object
    """
    rich_text_object = RichText()
    rich_text_object.add(
        text=company_dataframe.loc[
            company_name, "webSiteAlias"
        ],  # specifying the display text
        url_id=template.build_url_id(
            company_dataframe.loc[
                company_name, "webSiteLink"
            ]  # specifying the embedded clickable URL
        ),
        color="blue",
        bold=True,
        underline=True,
        size=18,
    )
    print("Rich Text for weblink has been created successfully")
    return rich_text_object


def configure_rich_text_date_of_offer(
    candidate_dataframe: pd.DataFrame,
    candidate_index: int
) -> RichText:
    """
    This function is used for configuring the rich text object for
    embedding the superscript ordinal number of the day of a month
    for better readability.

    Args:
        candidate_dataframe (pd.DataFrame): The Pandas DataFrame containing candidate information
        candidate_index (int): The row index of the candidate in the dataframe
        logger_object (logging.Logger): The logger object which is used to log the information

    Returns:
        The configured RichText object
    """
    rich_text_object = RichText()
    offer_date = candidate_dataframe.loc[candidate_index, "offerDate"].to_pydatetime()

    rich_text_object.add(
        text=offer_date.day,
        size=22,
        color="black",
    )

    rich_text_object.add(
        text=get_position_of_a_day(offer_date.day),
        size=22,
        color="black",
        superscript=True,
    )  # for superscripting the position of the day

    rich_text_object.add(
        text=offer_date.strftime(DEFAULT_OFFER_DATE_MONTH_YEAR_FORMAT),
        size=22,
        color="black",
    )
    print("Rich Text for offer date has been created successfully")
    return rich_text_object


def get_file_extension(file_name: str):
    """
    This function accepts the file name and returns the extension of the file
    Args:
        file_name (str): The file name

    Returns:
        The extension of the `file_name`
    """
    pattern = re.compile(r"([\w\\/]*?)(\w+)\.(\w+)")
    match = re.match(pattern, file_name)
    return match.group(3) if match else ""


def get_automapped_numeric_and_string_context(
    dataframe: pd.DataFrame, row_identifier: Any
):
    """


    Args:
        dataframe (pd.DataFrame): The Pandas DataFrame containing information of company/candidate.
        row_identifier (str): The identifier to uniquely identify each row of the `dataframe`

    Returns:
        It returns dictionary containing auto-mapped information of company/candidate.
        Here, by auto-mapping means dataframe's column-headers are used as the keys of the context dictionary
    """
    numeric_and_string_context: dict = {}
    for column_header in dataframe.columns:
        if dataframe[column_header].dtype == "int64":
            numeric_and_string_context[column_header] = locale.format_string(
                f="%d",
                val=dataframe.loc[row_identifier, column_header],
                grouping=True,
            )
        elif dataframe[column_header].dtype == "object" and not (
            get_file_extension(file_name=dataframe.loc[row_identifier, column_header])
            in ACCEPTABLE_IMAGE_FORMATS
        ):
            numeric_and_string_context[column_header] = dataframe.loc[
                row_identifier, column_header
            ]

    return numeric_and_string_context


def populate_candidate_context(
    template: DocxTemplate,
    candidate_dataframe: pd.DataFrame,
    candidate_index: int
) -> dict:
    """

    Args:
        template (DocxTemplate): The DocxTemplate object which holds template information
        candidate_dataframe (pd.DataFrame): The Pandas DataFrame containing candidate information
        candidate_index (int): The row index of the candidate in the dataframe

    Returns:
        a dictionary populated with the details of the candidate information whose row index in the dataframe
        matches with the parameter `row_identifier`
    """
    context: dict = {"candidateName": ""}
    try:
        context = (
            context
            | get_automapped_numeric_and_string_context(
                dataframe=candidate_dataframe, row_identifier=candidate_index
            )
            | {
                "ctcInWord": (
                    num2words(
                        number=candidate_dataframe.loc[
                            candidate_index, "totalCtcPerYear"
                        ],
                        lang=DEFAULT_NUM2WORDS_LANGUAGE,
                    )
                    .title()
                    .replace(",", "")
                ),  # title styling i.e. first letter of each word in upper case
                "candidateSignature": InlineImage(
                    tpl=template,
                    image_descriptor=IMAGE_PATH
                    + candidate_dataframe.loc[
                        candidate_index, "candidateSignature"  # path to the image
                    ],
                    height=CANDIDATE_SIGNATURE_IMG_HEIGHT,
                    width=CANDIDATE_SIGNATURE_IMG_WIDTH,
                ),
            }
        )

        print(
            f"Candidate Context has been generated successfully for candidate number {candidate_index}"
        )
    except KeyError:
        print("Check keys to access data from the dataframe")
    # except Exception:
    
    finally:
        return context


def populate_company_context(
    template: DocxTemplate,
    company_dataframe: pd.DataFrame,
    company_name: str
) -> dict:
    """
    This function takes the Dataframe having company information in it along with
    the name of the company and returns a dictionary containing the company information
    whose name is specified with the `company_name`

    Args:
        template (DocxTemplate): The DocxTemplate object which holds template information
        company_dataframe (pd.DataFrame): The Pandas DataFrame containing company information
        company_name (str): Name of the company

    Returns:
        a dictionary populated with the details of the company information whose name matches
        with the parameter`company_name`
    """
    context: dict = {"companyName": ""}
    try:
        context = (
            context | get_automapped_numeric_and_string_context(
                dataframe=company_dataframe, row_identifier=company_name
            )
            | {
                "companyName": company_name,
                "companyLogo": InlineImage(
                    tpl=template,
                    image_descriptor=IMAGE_PATH
                    + company_dataframe.loc[
                        company_name, "companyLogo"
                    ],  # path to the image
                    height=COMPANY_LOGO_IMG_HEIGHT,
                    width=COMPANY_LOGO_IMG_WIDTH,
                ),
                "hrSignature": InlineImage(
                    tpl=template,
                    image_descriptor=IMAGE_PATH
                    + company_dataframe.loc[
                        company_name, "hrSignature"
                    ],  # path to the image
                    height=HR_SIGNATURE_IMG_HEIGHT,
                    width=HR_SIGNATURE_IMG_WIDTH,
                ),
            }
        )
        print(
            f"Company Context has been generated successfully for the company {company_name}"
        )
    except KeyError:
        print("Check keys to access data from the dataframe")
    # except Exception:
    
    finally:
        return context


def render_and_produce_PDF(
    template: DocxTemplate,
    context_information: dict,
    candidate_name: str
) -> None:
    """
    This function renders the `context_information` in the template and produces
    LOIs in pdf format with name as `<candidate_name>_LOI.pdf`

    Args:
        template (DocxTemplate): The DocxTemplate object which holds template information
        context_information (dict): Dictionary containing information that is to be rendered in the template
        candidate_name (str): Name of the candidate for which offer letter is to be generated
    """
    candidate_name = candidate_name.strip().replace(" ", "_")
    template.render(
        context=context_information
    )  # rendering the context information in the template
    print(
        f"The context information has been rendered successfully to the template for the candidate {candidate_name}"
    )

    template.save(
        OUTPUT_DOCX_ROOT_PATH + candidate_name + OUTPUT_FILE_ENDING_FORMAT + ".docx"
    )  # saving the populated docx file
    print(
        f"The word document has been generated successfully for the candidate {candidate_name}"
    )
    docx2pdf.convert(
        input_path=OUTPUT_DOCX_ROOT_PATH
        + candidate_name
        + OUTPUT_FILE_ENDING_FORMAT
        + ".docx",
        output_path=OUTPUT_PDF_ROOT_PATH
        + candidate_name
        + OUTPUT_FILE_ENDING_FORMAT
        + ".pdf",
    )  # converting the produced *.docx files to PDF files
    print(
        f"The pdf loi has been generated successfully for the candidate {candidate_name}"
    )


def main(company_name: str) -> None:
    
    """
    This function takes the company name and produces LOIs in pdf format for that company.
    Find pdf files in `/output/pdf/` directory and
    Find document files in `/output/document/` directory inside the root directory

    Args:
        company_name (str): Name of the company for which LOIs should be produced
    """
    
    # Setting the locale to en_IN with character encoding UTF-8
    locale.setlocale(category=LOCALE_CATEGORY, locale=LOCALE_TYPE)

    # Initializing the Document Template by specifying the path to the template document file
    document: DocxTemplate = DocxTemplate(DOCX_TEMPLATE_PATH)

    # Reading the Candidate Information to a pandas dataframe
    try:
        candidate_information: pd.DataFrame = pd.read_excel(CANDIDATE_SHEET_PATH)
    except Exception as e:
        print(e)
    print(candidate_information)
    # Reading the Company Information to a pandas dataframe.
    # The companyName column in the Dataframe is treated as Index.
    company_information: pd.DataFrame = pd.read_excel(
        COMPANY_SHEET_PATH, index_col="companyName"
    )
    
    # getting the company information
    company_context = populate_company_context(
        template=document,
        company_dataframe=company_information,
        company_name=company_name
    )
    print("i am here")
    for candidate_index in range(len(candidate_information)):
        # Initializing the rich text object for embedding a URL in the document.
        # the URL is used for specifying the website of the company which is clickable
        rich_text_web_link = configure_rich_text_web_link(
            template=document,
            company_dataframe=company_information,
            company_name=company_name
        )

        # Configuring Rich Text Object for date of offer
        rich_text_date_of_offer = configure_rich_text_date_of_offer(
            candidate_dataframe=candidate_information,
            candidate_index=candidate_index
        )

        # getting the candidate information
        candidate_context = populate_candidate_context(
            template=document,
            candidate_dataframe=candidate_information,
            candidate_index=candidate_index
        )
        # merging both the candidate and company information along with
        # the rich text objects
        context :dict = {
            **candidate_context,
            **company_context,
            "todayDate": datetime.date.today().strftime(DEFAULT_DATE_TIME_FORMAT),
            "webSiteLink": rich_text_web_link,
            "offerDate": rich_text_date_of_offer,
        }
        print("i am here")
        render_and_produce_PDF(
            template=document,
            context_information=context,
            candidate_name=candidate_context["candidateName"] or "CORRUPTED"
        )
        print("i am here")
        print(candidate_context)
        if candidate_context["candidateName"]:
            print("i am here")
            print(
                "LOI for %s has been generated" % candidate_context["candidateName"]
            )

    print("LoiProducer has successfully produced all the LOIs")


if __name__ == "__main__":
    try:
        print("COMPANY_NAME")
        main(company_name=COMPANY_NAME)
        
    except Exception:
        print("An unexpected error has occurred")
