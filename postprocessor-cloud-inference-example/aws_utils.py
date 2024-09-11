import boto3

rekognition_client = None

def create_session(logger, rekognition_client = None):

    logger.info("Creating session to AWS")

    try:
        # create configuration in ~/.aws/credentials
        #
        # [default]
        # aws_access_key_id=acced_key
        # aws_secret_access_key=secret_access_key

        session = boto3.Session()

        new_rekognition_client = session.client('rekognition')

        logger.info("Created session rekognition to AWS")

    except Exception as e:
        logger.error(f"Error: {e}")

    return new_rekognition_client


def classify_faces(image_path, logger):

    global rekognition_client

    if rekognition_client is None:
        rekognition_client = create_session(logger)

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
        logger.error(f"Error: {e}")
        return None


def age_to_word(ager_range):
    age = (ager_range['Low'] + ager_range['High']) / 2

    age = int((age // 10) * 10)

    return f'{age}s'