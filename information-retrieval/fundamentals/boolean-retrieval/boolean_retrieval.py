# Part 1: InvertedIndex
import os
import collections
import re



class InvertedIndex:
    def __init__(self, collection_path):
        """
        Initialize the inverted index from the AP collection.

        During index construction, specifically, for building the posting lists you should use successive integers as
        document internal identifiers (IDs) for optimizing query processing, as taught in class, but you still need to
        be able to get the original document ID when required.

        :param collection_path: path to the AP collection
        """
        self.collection_path = collection_path
        self.doc_nums_to_ids = {}  # Map original DOCNO to internal ID
        self.ids_to_doc_nums = {}  # Map internal ID to original DOCNO
        self.last_index_doc_num = 0  # Current internal ID
        self.postings = {}  # Inverted index: term -> list of internal IDs
        pass

    def read_collection(self):
        """
        Read the AP collection and build the inverted index.
        :return: None
        """
        for doc in os.listdir(self.collection_path):
            with open(os.path.join(self.collection_path, doc), 'r') as f:
                content = f.read().replace('\n', '')
                # Extract DOCNO and TEXT
                inner_docs = content.split('</DOC>')
                for inner_doc in inner_docs:
                    inner_doc = inner_doc.strip()
                    if inner_doc:
                        # Extract DOCNO and TEXT
                        docno = self.extract_docno(inner_doc)
                        if docno:
                            # Assign internal ID
                            if docno not in self.doc_nums_to_ids:
                                self.doc_nums_to_ids[docno] = self.last_index_doc_num
                                self.ids_to_doc_nums[self.last_index_doc_num] = docno
                                self.last_index_doc_num += 1
                                text = self.extract_text(inner_doc)
                                if text:
                                    # Tokenize and build posting list
                                    words = text.split()
                                    unique_tokens = set(words)
                                    for token in unique_tokens:
                                        if token not in self.postings:
                                            self.postings[token] = []
                                        self.postings[token].append(self.doc_nums_to_ids[docno])

    def extract_docno(self, content):
        """
        Extract the DOCNO from the content.
        :param content: the document content
        :return: the DOCNO
        """
        match = re.search(r'<DOCNO>(.*?)</DOCNO>', content)
        return match.group(1).strip() if match else None

    def extract_text(self, content):
        """
        Extract the TEXT from the content.
        :param content: the document content
        :return: the TEXT
        """
        match = re.findall(r'<TEXT>(.*?)</TEXT>', content)
        return ' '.join(match).strip() if match else None

    def get_posting_list(self, term):
        """
        Return the posting list for the given term from the index.
        If the term is not in the index, return an empty list.
        :param term: a word
        :return: list of document ids in which the term appears
        """
        return self.postings[term]


# Part 2: Boolean Retrieval Model
class BooleanRetrieval:
    def __init__(self, inverted_index):
        self.index = inverted_index
        pass

    def run_query(self, query):
        """
        Run the given query on the index.
        :param query: a boolean query
        :return: list of document docnos
        """
        stack = []

        #in case of single word query
        if len(query.split())==1:
            relevant = self.index.postings.get(query.lower(), [])
            stack.append(relevant)

        # in case of multyple word query (RPM)
        else:
            for token in query.split():
                if token in {"AND", "OR", "NOT"}:
                    list2 = stack.pop()
                    if stack == []:
                        list1 = list(self.index.doc_nums_to_ids.values())
                        stack.append(list1)
                    list1 = stack.pop()
                    if token == "AND":
                        stack.append(self.intersect(list1, list2))
                    elif token == "OR":
                        stack.append(self.union(list1, list2))
                    elif token == "NOT":
                        stack.append(self.difference(list1, list2))
                else:
                    relevant = self.index.postings.get(token.lower(), [])
                    stack.append(relevant)
        #converte ID's to DOCNOS
        docnos = [self.index.ids_to_doc_nums[i] for i in stack[0]]
        return docnos

    def merge(self, list1, list2, condition):
        # Merge two sorted lists based on a condition
        i, j = 0, 0
        result = []
        while i < len(list1) and j < len(list2):
            if list1[i] == list2[j]:
                # If elements are equal, check if we should include them
                if condition('equal'):
                    result.append(list1[i])
                i += 1
                j += 1
            elif list1[i] < list2[j]:
                if condition('left'):
                    result.append(list1[i])
                i += 1
            else:
                if condition('right'):
                    result.append(list2[j])
                j += 1

        # Add remaining elements from list1 if needed
        while i < len(list1):
            if condition('left'):
                result.append(list1[i])
            i += 1

        while j < len(list2):
            if condition('right'):
                result.append(list2[j])
            j += 1

        return result

    def intersect(self, list1, list2):
        # Return only elements present in both lists
        return self.merge(list1, list2, lambda case: case == 'equal')

    def union(self, list1, list2):
        # Return all elements from both lists (no duplicates)
        return self.merge(list1, list2, lambda case: case in {'equal', 'left', 'right'})

    def difference(self, list1, list2):
        # Return elements only from list1 (excluding elements also in list2)
        return self.merge(list1, list2, lambda case: case == 'left')





if __name__ == "__main__":

    #path_to_AP_collection = './data'
    #path_to_boolean_queries = './BooleanQueries.txt'

    path_to_AP_collection = '/data/HW1/AP_Coll_Parsed'
    path_to_boolean_queries = '/data/HW1/BooleanQueries.txt'


    # Part 1
    inverted_index = InvertedIndex(path_to_AP_collection)
    inverted_index.read_collection()

    # Part 2
    boolean_retrieval = BooleanRetrieval(inverted_index=inverted_index)
    # Read queries from file
    with open(path_to_boolean_queries, 'r') as f:
        queries = f.readlines()
    queries = [q.strip() for q in queries]

    # Run queries and write results to file
    with open("Part_2.txt", 'w') as f:
        for query in queries:
            result = boolean_retrieval.run_query(query)
            f.write(' '.join(result) + '\n')

    # Part 3
    # Sort keys by the length of their value list, descending
    sorted_terms = sorted(inverted_index.postings, key=lambda k: (len(inverted_index.postings[k]), k), reverse=True)

    with open("Part_3a.txt", 'w') as f:
        for term in sorted_terms[:10]:
            f.write(term + ': ' + str(len(inverted_index.postings[term])) +'\n')

    with open("Part_3b.txt", 'w') as f:
        for term in sorted_terms[-10:]:
            f.write(term + ': ' + str(len(inverted_index.postings[term])) +'\n')