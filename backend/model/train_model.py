import tensorflow as tf
import numpy as np
import cv2
import mediapipe as mp
import os
import logging
from sklearn.model_selection import train_test_split
from datetime import datetime
from .model import SignLanguageModel

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SignLanguageDataset:
    def __init__(self, data_dir):
        """
        Initialize the dataset loader
        
        Args:
            data_dir: Directory containing the training data
        """
        self.data_dir = data_dir
        self.mp_hands = mp.solutions.hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.7
        )
        
    def load_data(self):
        """
        Load and preprocess the dataset
        
        Returns:
            X: Features (hand landmarks)
            y: Labels (sign classes)
        """
        X = []
        y = []
        
        # Iterate through each class directory
        for class_idx, class_name in enumerate(sorted(os.listdir(self.data_dir))):
            class_dir = os.path.join(self.data_dir, class_name)
            if not os.path.isdir(class_dir):
                continue
                
            logger.info(f"Processing class: {class_name}")
            
            # Process each image in the class directory
            for img_name in os.listdir(class_dir):
                img_path = os.path.join(class_dir, img_name)
                
                try:
                    # Read and process image
                    img = cv2.imread(img_path)
                    if img is None:
                        continue
                        
                    # Convert BGR to RGB
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    
                    # Extract hand landmarks
                    landmarks = self._extract_landmarks(img_rgb)
                    if landmarks is not None:
                        X.append(landmarks)
                        y.append(class_idx)
                        
                except Exception as e:
                    logger.error(f"Error processing {img_path}: {str(e)}")
                    continue
        
        return np.array(X), np.array(y)
    
    def _extract_landmarks(self, image):
        """
        Extract hand landmarks from an image
        
        Args:
            image: Input RGB image
            
        Returns:
            Normalized landmarks array or None if no hand detected
        """
        results = self.mp_hands.process(image)
        
        if results.multi_hand_landmarks:
            # Get the first detected hand
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Extract and normalize landmarks
            landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
            
            # Normalize the coordinates
            landmarks = self._normalize_landmarks(landmarks)
            
            return landmarks
        return None
    
    def _normalize_landmarks(self, landmarks):
        """
        Normalize the landmarks to be invariant to scale and translation
        
        Args:
            landmarks: Array of landmarks
            
        Returns:
            Normalized landmarks array
        """
        # Center the landmarks
        center = np.mean(landmarks, axis=0)
        centered = landmarks - center
        
        # Scale to unit size
        scale = np.max(np.abs(centered))
        normalized = centered / scale
        
        return normalized

def train_model(data_dir, model_save_path, epochs=50, batch_size=32):
    """
    Train the sign language recognition model
    
    Args:
        data_dir: Directory containing the training data
        model_save_path: Path to save the trained model
        epochs: Number of training epochs
        batch_size: Batch size for training
    """
    try:
        # Load and preprocess data
        logger.info("Loading dataset...")
        dataset = SignLanguageDataset(data_dir)
        X, y = dataset.load_data()
        
        # Convert labels to one-hot encoding
        num_classes = len(np.unique(y))
        y = tf.keras.utils.to_categorical(y, num_classes)
        
        # Split data into train and validation sets
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        logger.info(f"Dataset split - Training: {len(X_train)}, Validation: {len(X_val)}")
        
        # Initialize and build the model
        model = SignLanguageModel()
        model.build_model()
        
        # Create callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ModelCheckpoint(
                filepath=os.path.join(model_save_path, 'checkpoint_{epoch:02d}.h5'),
                save_best_only=True,
                monitor='val_accuracy'
            ),
            tf.keras.callbacks.TensorBoard(
                log_dir=os.path.join(model_save_path, 'logs', datetime.now().strftime("%Y%m%d-%H%M%S")),
                histogram_freq=1
            )
        ]
        
        # Train the model
        logger.info("Starting model training...")
        history = model.train(
            X_train,
            y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks
        )
        
        # Evaluate the model
        loss, accuracy = model.evaluate(X_val, y_val)
        logger.info(f"Validation Loss: {loss:.4f}")
        logger.info(f"Validation Accuracy: {accuracy:.4f}")
        
        # Save the final model
        model_path = os.path.join(model_save_path, 'final_model.h5')
        model.save_model(model_path)
        logger.info(f"Model saved to {model_path}")
        
        return history
        
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        raise

if __name__ == "__main__":
    # Configuration
    DATA_DIR = "path/to/your/dataset"  # Update this path
    MODEL_SAVE_PATH = "backend/model/saved_model"
    
    # Create model save directory if it doesn't exist
    os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
    
    # Train the model
    try:
        history = train_model(DATA_DIR, MODEL_SAVE_PATH)
        logger.info("Training completed successfully!")
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
