from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

sentence = "This is a test sentence for embedding."

embedding = model.encode(sentence)
print(f"Embedding for the sentence: {embedding}")

similarities = model.encode(["This is a test sentence for embedding.", "This is another sentence."])
print(f"Similarities: {similarities}")