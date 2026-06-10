import pickle


with open(
    "data/processed/chunks.pkl",
    "rb"
) as f:

    chunks = pickle.load(f)

print(f"\nTotal Chunks: {len(chunks)}")

print("\n" + "=" * 100)
print("CHUNK 1")
print("=" * 100)

print(chunks[0])

print("\n" + "=" * 100)
print("CHUNK 2")
print("=" * 100)

print(chunks[1])

print("\n" + "=" * 100)
print("CHUNK 3")
print("=" * 100)

print(chunks[2])