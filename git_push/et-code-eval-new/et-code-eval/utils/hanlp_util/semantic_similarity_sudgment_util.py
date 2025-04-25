# 语义相似判断
import os


class SemanticSimilarityJudgmentUtil:

    def __init__(self):
        model_dir = os.path.join(".", "sts_electra_base_zh_20210530_200109")
        # 打印model_dir的绝对路径
        from hanlp.components.sts.transformer_sts import TransformerSemanticTextualSimilarity
        similarity = TransformerSemanticTextualSimilarity()
        similarity.load(model_dir)
        self.__sim = similarity

    def get_similarity(self, text1, text2):
        data = [text1, text2]
        return self.__sim(data)
