"""
Start the Ethio Car Equb admin dashboard.
Run: python run_dashboard.py
"""

import uvicorn

from config import DASHBOARD_HOST, DASHBOARD_PORT

if __name__ == "__main__":
    uvicorn.run(
        "dashboard.app:app",
        host=DASHBOARD_HOST,
        port=DASHBOARD_PORT,
        reload=False,
    )
