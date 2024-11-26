import qrcode
import io
import base64
from typing import Dict
from fastapi import HTTPException

class QRGenerator:
    @staticmethod
    def generate_item_qr(item_data: Dict) -> str:
        """
        Generate a QR code for an item and return it as a base64 encoded string.

        Args:
            item_data: Dictionary containing item details (id, name, price)

        Returns:
            str: Base64 encoded PNG image of the QR code
        """
        try:
            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )

            # Add data to QR code
            qr_data = {
                "id": item_data["id"],
                "name": item_data["name"],
                "price": str(item_data["price"])
            }
            qr.add_data(str(qr_data))
            qr.make(fit=True)

            # Create image from QR code
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert image to base64
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_str = base64.b64encode(img_buffer.getvalue()).decode()

            return f"data:image/png;base64,{img_str}"

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating QR code: {str(e)}"
            )

    @staticmethod
    def generate_batch_qr_codes(items: list[Dict]) -> list[Dict]:
        """
        Generate QR codes for multiple items.

        Args:
            items: List of dictionaries containing item details

        Returns:
            list: List of dictionaries with item details and QR codes
        """
        qr_codes = []
        for item in items:
            qr_code = QRGenerator.generate_item_qr(item)
            qr_codes.append({
                "item_id": item["id"],
                "item_name": item["name"],
                "qr_code": qr_code
            })
        return qr_codes

qr_generator = QRGenerator()
