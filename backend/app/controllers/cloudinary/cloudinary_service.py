import cloudinary.uploader
import io
import base64
from PIL import Image


class CloudinaryService:
    def __init__(self):
        pass

    def compress_image(image_data, quality=85):
        img = Image.open(image_data)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        return buffer

    def upload_image(self, image_data):
        compressed_image = CloudinaryService.compress_image(image_data)
        result = cloudinary.uploader.upload(compressed_image, resource_tpye="image")
        return {"secure_url": result["secure_url"], "public_id": result["public_id"]}

    def base64_to_image_file(self, base64_str):
        image_data = base64.b64decode(base64_str)
        return io.BytesIO(image_data)

    def upload_multiple_images(self, images_base64):
        urls = []
        for image in images_base64[:5]:
            image_file = self.base64_to_image_file(image)
            if isinstance(image_file, io.BytesIO):
                result = self.upload_image(image_file)
                if isinstance(result, dict):
                    urls.append(result)
                else:
                    print(result)
        return urls

    def delete_image(self, public_id):
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result
        except Exception as e:
            return {"error": str(e)}
