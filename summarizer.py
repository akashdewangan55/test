from transformers import pipeline

# Load BART summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text, max_length=300, min_length=60):
    # Trim too-long texts to 1024 tokens (BART limit)
    trimmed_text = text[:3000]
    summary = summarizer(trimmed_text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']
