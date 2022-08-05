import os
import sys
from typing import List

import pandas as pd
import pytest
from docxtpl import DocxTemplate
import loi_producer_config


myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath)


@pytest.fixture(autouse=True)
def company_name():
    return "Celebal Technologies Private Limited"


@pytest.fixture()
def company_information():
    return pd.read_excel(
        loi_producer_config.COMPANY_SHEET_PATH,
        index_col="companyName",
    )


@pytest.fixture()
def fake_company_context() -> dict:
    return {
        "companyName": "Test Company Name",
        "companyAddress": "Test Company Address",
        "hrName": "Test HR Name",
        "hrMail": "Test HR Email",
        "salesMail": "Test Sales Email",
        "companyContact": "Test Company Contact",
        "webSiteLink": "Test Company Website",
        "webSiteAlias": "Test Company Website Alias",
        "companyLogo": "Test Company Logo",
    }


@pytest.fixture()
def candidate_information():
    return pd.read_excel(
        loi_producer_config.CANDIDATE_SHEET_PATH,
    )


@pytest.fixture()
def fake_candidate_context() -> dict:
    return {
        "candidateName": "Test Candidate Name",
        "location": "Test Candidate Location",
        "basic": "Test Candidate Basic",
        "hra": "Test Candidate HRA",
        "offerDate": "2022-09-01",
        "candidateSignature": "Test Candidate Signature"
    }


@pytest.fixture()
def fake_candidate_context_list() -> List[dict]:
    return [
        {
            "candidateName": "Test Candidate Name 1",
            "location": "Test Candidate Location 1",
            "basic": "Test Candidate Basic 1",
            "hra": "Test Candidate HRA 1",
            "offerDate": "2022-09-01",
            "candidateSignature": "Test Candidate Signature 1"
        },
        {
            "candidateName": "Test Candidate Name 2",
            "location": "Test Candidate Location 2",
            "basic": "Test Candidate Basic 2",
            "hra": "Test Candidate HRA 2",
            "offerDate": "2022-09-02",
            "candidateSignature": "Test Candidate Signature 2"
        }
    ]


@pytest.fixture()
def document_template():
    return DocxTemplate(
        loi_producer_config.DOCX_TEMPLATE_PATH
    )


@pytest.fixture()
def fake_document_template():
    return DocxTemplate(
        "tests/test_templates/test_loi_template.docx"
    )
