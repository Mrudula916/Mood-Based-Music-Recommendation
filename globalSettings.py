use_webcam = False
save_images = True
#DBPath = 'D:\\audio.db'
DBPath = 'audio.db'
useVGG = False

genres = {
    'metal': 0, 'disco': 1, 'classical': 2, 'hiphop': 3, 'jazz': 4, 
    'country': 5, 'pop': 6, 'blues': 7, 'reggae': 8, 'rock': 9
}

emotion_genre_mappings = {
    'Angry':['hiphop'], 
    'Disgust':['hiphop'], 
    'Fear':['classical','country'], 
    'Happy':['rock','pop'], 
    'Sad':['blues'], 
    'Surprise':['metal','country'], 
    'Neutral':['jazz','reggae']
}