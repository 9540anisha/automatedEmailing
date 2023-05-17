from transformers import GPT2TokenizerFast
import re
 
def split_file(text, max_tokens):
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

    sentence_boundary_pattern = r'(?<=[.!?])\s+(?=[^\d])'
    sentence_boundaries = [(m.start(), m.end()) for m in re.finditer(sentence_boundary_pattern, text)]
    
    chunks = []
    current_chunk = []
    current_token_count = 0
    current_position = 0
 
    for boundary_start, boundary_end in sentence_boundaries:
        sentence = text[current_position:boundary_start+1]
        current_position = boundary_end
 
        token_count = len(tokenizer(sentence)["input_ids"])
 
        if current_token_count + token_count <= max_tokens:
            current_chunk.append(sentence)
            current_token_count += token_count
        else:
            chunks.append(''.join(current_chunk))
            current_chunk = [sentence]
            current_token_count = token_count
 
    # Append the last sentence
    last_sentence = text[current_position:]
    current_chunk.append(last_sentence)
    chunks.append(''.join(current_chunk))
 
    return chunks
 
''' Only for testing purposes #'''
# def main():
#     # file_path = ''  # Replace with your input text file path
#     chunks = split_file(r'C:\Users\User\openai-quickstart-node\pages\api\paper.txt')
 
#     for i, chunk in enumerate(chunks):
#         with open(f'chunk_{i+1}.txt', 'w', encoding='utf-8') as output_file:
#             # output_file.write(chunk)
#             print(chunk + "\n ----------------------------- \n")
 
# if __name__ == '__main__':
#     main()