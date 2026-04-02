import hashlib
import bitarray
from typing import Set

class BloomFilter:
    def __init__(self, size: int = 1000000, hash_count: int = 5):
        """
        初始化布隆过滤器
        :param size: 位数组大小
        :param hash_count: 哈希函数个数
        """
        self.size = size
        self.hash_count = hash_count
        self.bit_array = bitarray.bitarray(size)
        self.bit_array.setall(0)
    
    def _get_hashes(self, item: str) -> list:
        """
        生成多个哈希值
        :param item: 要哈希的元素
        :return: 哈希值列表
        """
        hashes = []
        for i in range(self.hash_count):
            # 使用不同的种子生成不同的哈希值
            hash_obj = hashlib.md5(f"{item}:{i}".encode('utf-8'))
            hashes.append(int(hash_obj.hexdigest(), 16) % self.size)
        return hashes
    
    def add(self, item: str) -> None:
        """
        添加元素到布隆过滤器
        :param item: 要添加的元素
        """
        for hash_val in self._get_hashes(item):
            self.bit_array[hash_val] = 1
    
    def contains(self, item: str) -> bool:
        """
        判断元素是否在布隆过滤器中
        :param item: 要判断的元素
        :return: True表示可能存在，False表示一定不存在
        """
        for hash_val in self._get_hashes(item):
            if self.bit_array[hash_val] == 0:
                return False
        return True
    
    def add_batch(self, items: Set[str]) -> None:
        """
        批量添加元素
        :param items: 元素集合
        """
        for item in items:
            self.add(item)
