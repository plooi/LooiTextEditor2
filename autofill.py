


class AutoFill:
    def __init__(self, text_area):
        self.text_area = text_area
        
        
        self.token_frequencies = TokenFrequencies()
        self.token_starts = []
        self.token_values = []
    
    def clear(self):
        self.token_frequencies.clear()
        self.token_starts = []
        self.token_values = []
    def add_token(self, token_start, token_end, token):
        self.token_frequencies.add_token(token)
        # we assume that all tokens are added in order
        self.token_starts.append(token_start)
        self.token_values.append(token)
    def get_all_tokens_in_range(self, center, range):
        #center is an index in the text, comparable to the start indexes
        
        #find the token closest to the center
        index_of_token_closest_to_center = -1
        high = len(self.token_starts)-1
        low = 0
        while True:
            mid = (high+low)/2
            
            if high-low < 2:
                index_of_token_closest_to_center = low
                break
            
            
            if self.token_starts[mid] >= center:
                high = mid
            else:
                low = mid
                
        close_tokens_low = -1#index in token starts of the lowest token that counts as close
        close_token_high = -1#index in token starts of the lowest token that counts as close
        
        
        i = 0
        while True:
            index = index_of_token_closest_to_center - i
            
            if self.token_starts[index] > center - range:
                pass
            #wip
        
        
        
    def autofill(self, prefix):
        possibilities = get_all_tokens_that_start_with()
    
        
class TokenFrequencies:
    def __init__(self):
        self.d = {}
        
    def clear(self):
        self.d = {}
        
    def add_token(self, token):
        if token == None or len(token) == 0: return
        start_char = token[0]
        if start_char not in self.d: self.d[start_char] = {}
        if token not in self.d[start_char]: self.d[start_char][token] = 0
        self.d[start_char][token] += 1
        
    def get_all_tokens_that_start_with(self, prefix):
        start_char = prefix[0]
        
        tokens_with_start_char = self.d[start_char]
        
        ret = set()
        
        for token in tokens_with_start_char:
            if token.startswith(prefix):
                ret.add(token)
        
        return ret
    def get_frequency(self, token):
        start_char = token[0]
        return self.d[start_char][token]
        
        
def main():
    tf = TokenFrequencies()
    tf.add_token("public")
    tf.add_token("public")
    tf.add_token("public")
    tf.add_token("public")
    tf.add_token("class")
    tf.add_token("print")
    print(tf.get_all_tokens_that_start_with("pu"))
if __name__ == "__main__": main()