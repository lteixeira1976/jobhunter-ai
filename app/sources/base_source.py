from abc import ABC, abstractmethod


class JobSource(ABC):


    @abstractmethod
    def search(self, keyword: str):
        pass