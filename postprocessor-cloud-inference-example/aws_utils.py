import json
import boto3
from botocore.exceptions import ClientError

session = boto3.Session(
    aws_access_key_id='',  # Specify your access key
    aws_secret_access_key='', # Specify your secret key
    region_name='us-east-1'  # Specify your region
)

rekognition_client = session.client('rekognition')

def classify_faces(image_path):
    try:
        with open(image_path, 'rb') as image:
            response = rekognition_client.detect_faces(
                Image={
                    'Bytes': image.read()
                },
                Attributes=['GENDER', 'EMOTIONS', 'AGE_RANGE', 'SUNGLASSES', 'SMILE']
            )
        faces = response['FaceDetails']
        for face in faces:
            age_range = face['AgeRange']
            gender = face['Gender']
            smile = face['Smile']
            sun_glasses = face['Sunglasses']
            emotions = face['Emotions']

        age = age_to_word(age_range)
        his_her = 'his' if gender['Value'].lower() == 'male' else 'her'
        description = f"A {gender['Value'].lower()} in {his_her} {age} feeling {emotions[0]['Type'].lower()}."
        return description

    except Exception as e:
        print(f"Error: {e}")
        return None


def age_to_word(ager_range):
    age = (ager_range['Low'] + ager_range['High']) / 2

    age = int((age // 10) * 10)

    return f'{age}s'