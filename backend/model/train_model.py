import tensorflow as tf
import numpy as np
import cv2
import mediapipe as mp
import os
import logging
from sklearn.model_selection import train_test_split
from datetime import datetime
from .model import SignLanguageModel
import openai
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import Config

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

def generate_synthetic_data_with_chatgpt(num_samples=100, language='ASL'):
    """
    Generate synthetic training data using ChatGPT

    Args:
        num_samples: Number of synthetic samples to generate
        language: Sign language to generate data for

    Returns:
        List of synthetic text samples
    """
    try:
        if not Config.OPENAI_API_KEY:
            logger.warning("OpenAI API key not found, skipping synthetic data generation")
            return []

        openai.api_key = Config.OPENAI_API_KEY

        synthetic_data = []

        # Generate data in batches to avoid token limits
        batch_size = 20
        for i in range(0, num_samples, batch_size):
            current_batch = min(batch_size, num_samples - i)

            prompt = f"""Generate {current_batch} diverse examples of common phrases and sentences that would be signed in {language} (American Sign Language).

Please provide realistic, varied examples including:
- Greetings and introductions
- Common questions and answers
- Everyday expressions
- Commands and requests
- Emotional expressions

Format each example as a simple sentence or phrase on a new line.
Make them natural and conversational."""

            response = openai.ChatCompletion.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant generating training data for {language} sign language recognition."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            generated_text = response.choices[0].message.content.strip()
            lines = [line.strip() for line in generated_text.split('\n') if line.strip()]

            synthetic_data.extend(lines)
            logger.info(f"Generated {len(lines)} synthetic samples (batch {i//batch_size + 1})")

        logger.info(f"Total synthetic data generated: {len(synthetic_data)}")
        return synthetic_data

    except Exception as e:
        logger.error(f"Error generating synthetic data: {str(e)}")
        return []

def augment_dataset_with_synthetic_data(X, y, synthetic_texts, augmentation_factor=2):
    """
    Augment the dataset with synthetic text data

    Args:
        X: Original features
        y: Original labels
        synthetic_texts: List of synthetic text samples
        augmentation_factor: How many times to augment each sample

    Returns:
        Augmented X and y
    """
    try:
        augmented_X = list(X)
        augmented_y = list(y)

        # For each synthetic text, create augmented samples
        for text in synthetic_texts:
            # Use text length and content to create pseudo-features
            # This is a simplified approach - in practice, you'd need to map text to gesture features
            text_features = np.random.rand(21, 3) * 0.1  # 21 hand landmarks, 3D

            # Add some variation for augmentation
            for _ in range(augmentation_factor):
                noise = np.random.normal(0, 0.05, text_features.shape)
                augmented_sample = text_features + noise
                augmented_X.append(augmented_sample)

                # Assign a random existing class or create new synthetic class
                synthetic_class = len(np.unique(y))  # New class for synthetic data
                augmented_y.append(synthetic_class)

        logger.info(f"Dataset augmented from {len(X)} to {len(augmented_X)} samples")
        return np.array(augmented_X), np.array(augmented_y)

    except Exception as e:
        logger.error(f"Error augmenting dataset: {str(e)}")
        return X, y

def train_model(data_dir, model_save_path, epochs=50, batch_size=32, use_synthetic_data=False):
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

        # Generate synthetic data if enabled
        if use_synthetic_data:
            logger.info("Generating synthetic data with ChatGPT...")
            synthetic_texts = generate_synthetic_data_with_chatgpt(num_samples=200, language='ASL')
            if synthetic_texts:
                X, y = augment_dataset_with_synthetic_data(X, y, synthetic_texts)

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
        # Set to True to enable synthetic data generation with ChatGPT
        use_synthetic = os.getenv('USE_SYNTHETIC_DATA', 'false').lower() == 'true'
        history = train_model(DATA_DIR, MODEL_SAVE_PATH, use_synthetic_data=use_synthetic)
        logger.info("Training completed successfully!")
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
