from abc import ABC, abstractmethod

class PlatformInterface(ABC):
    """
    Abstract base class for platform-specific implementations.
    """

    @abstractmethod
    def get_latest_installation(self, user):
        """
        Get the latest installation for the given user.
        """
        pass

    @abstractmethod
    def get_category(self, installation):
        """
        Get the category for the given installation.
        """
        pass

    @abstractmethod
    def generate_content(self, installation, plan):
        """
        Generate content based on the installation and plan.
        """
        pass

    @abstractmethod
    def sync_content(self, content):
        """
        Sync generated content to the platform.
        """
        pass
