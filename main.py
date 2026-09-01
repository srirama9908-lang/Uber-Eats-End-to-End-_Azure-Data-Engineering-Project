from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.security import APIKeyHeader
from typing import Optional
from datetime import datetime
import json
import os


# =========================================================
# API CONFIGURATION
# =========================================================

API_KEY = os.getenv(
    "API_KEY",
    "ubereats-demo-key-123"
)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Uber Eats Mock API",
    description="Mock REST API for Uber Eats Data Engineering Project",
    version="1.0"
)


# =========================================================
# API KEY SECURITY
# =========================================================

api_key_header = APIKeyHeader(
    name="X-API-Key",
    description="Enter your Uber Eats API key"
)


def verify_api_key(
    api_key: str = Depends(api_key_header)
):

    if api_key != API_KEY:

        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return api_key


# =========================================================
# LOAD JSON FILE
# =========================================================

def load_json_file(file_name):

    file_path = os.path.join(
        "data",
        file_name
    )

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except FileNotFoundError:

        raise HTTPException(
            status_code=500,
            detail=f"File not found: {file_path}"
        )

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON file: {file_path}"
        )


# =========================================================
# GENERIC DATA PROCESSING
# =========================================================

def process_data(
    file_name,
    timestamp_column,
    page,
    page_size,
    updated_after: Optional[str] = None
):

    # -----------------------------------------------------
    # Load JSON data
    # -----------------------------------------------------

    data = load_json_file(file_name)


    # -----------------------------------------------------
    # Incremental filtering
    # -----------------------------------------------------

    if updated_after:

        try:

            filter_date = datetime.fromisoformat(
                updated_after.replace(
                    "Z",
                    "+00:00"
                )
            )

        except ValueError:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid updated_after format. "
                    "Use YYYY-MM-DDTHH:MM:SS"
                )
            )


        filtered_data = []


        for record in data:

            # Skip records without timestamp

            if timestamp_column not in record:

                continue


            try:

                record_date = datetime.fromisoformat(
                    record[timestamp_column].replace(
                        "Z",
                        "+00:00"
                    )
                )

            except ValueError:

                continue


            # Incremental condition

            if record_date > filter_date:

                filtered_data.append(record)


        data = filtered_data


    # -----------------------------------------------------
    # Total records
    # -----------------------------------------------------

    total_records = len(data)


    # -----------------------------------------------------
    # Pagination
    # -----------------------------------------------------

    start_index = (
        page - 1
    ) * page_size

    end_index = (
        start_index + page_size
    )

    paginated_data = data[
        start_index:end_index
    ]


    # -----------------------------------------------------
    # Total pages
    # -----------------------------------------------------

    if total_records > 0:

        total_pages = (
            total_records
            + page_size
            - 1
        ) // page_size

    else:

        total_pages = 0


    # -----------------------------------------------------
    # API RESPONSE
    # -----------------------------------------------------

    return {

        "data": paginated_data,

        "pagination": {

            "page": page,

            "page_size": page_size,

            "total_records": total_records,

            "total_pages": total_pages
        }
    }


# =========================================================
# HOME ENDPOINT
# =========================================================

@app.get("/")
def home():

    return {

        "message": "Uber Eats Mock API is running",

        "version": "1.0",

        "endpoints": [

            "/payments",

            "/deliveries",

            "/ratings",

            "/order-status"
        ]
    }


# =========================================================
# PAYMENTS API
# =========================================================

@app.get(
    "/payments",
    tags=["Payments"]
)
def get_payments(

    page: int = Query(
        1,
        ge=1,
        description="Page number"
    ),

    page_size: int = Query(
        5,
        ge=1,
        le=100,
        description="Number of records per page"
    ),

    updated_after: Optional[str] = Query(
        None,
        description=(
            "Return records after this timestamp"
        )
    ),

    api_key: str = Depends(
        verify_api_key
    )
):

    return process_data(

        file_name="payments.json",

        timestamp_column="updated_at",

        page=page,

        page_size=page_size,

        updated_after=updated_after
    )


# =========================================================
# DELIVERIES API
# =========================================================

@app.get(
    "/deliveries",
    tags=["Deliveries"]
)
def get_deliveries(

    page: int = Query(
        1,
        ge=1,
        description="Page number"
    ),

    page_size: int = Query(
        5,
        ge=1,
        le=100,
        description="Number of records per page"
    ),

    updated_after: Optional[str] = Query(
        None,
        description=(
            "Return records after this timestamp"
        )
    ),

    api_key: str = Depends(
        verify_api_key
    )
):

    return process_data(

        file_name="deliveries.json",

        timestamp_column="updated_at",

        page=page,

        page_size=page_size,

        updated_after=updated_after
    )


# =========================================================
# RATINGS API
# =========================================================

@app.get(
    "/ratings",
    tags=["Ratings"]
)
def get_ratings(

    page: int = Query(
        1,
        ge=1,
        description="Page number"
    ),

    page_size: int = Query(
        5,
        ge=1,
        le=100,
        description="Number of records per page"
    ),

    updated_after: Optional[str] = Query(
        None,
        description=(
            "Return records after this timestamp"
        )
    ),

    api_key: str = Depends(
        verify_api_key
    )
):

    return process_data(

        file_name="ratings.json",

        timestamp_column="updated_at",

        page=page,

        page_size=page_size,

        updated_after=updated_after
    )


# =========================================================
# ORDER STATUS API
# =========================================================

@app.get(
    "/order-status",
    tags=["Order Status"]
)
def get_order_status(

    page: int = Query(
        1,
        ge=1,
        description="Page number"
    ),

    page_size: int = Query(
        5,
        ge=1,
        le=100,
        description="Number of records per page"
    ),

    updated_after: Optional[str] = Query(
        None,
        description=(
            "Return status events after this timestamp"
        )
    ),

    api_key: str = Depends(
        verify_api_key
    )
):

    return process_data(

        file_name="order_status.json",

        timestamp_column="status_timestamp",

        page=page,

        page_size=page_size,

        updated_after=updated_after
    )