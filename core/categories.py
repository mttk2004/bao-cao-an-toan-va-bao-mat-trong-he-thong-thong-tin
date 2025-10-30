# auracrypt2/core/categories.py
"""
Module quản lý categories (danh mục) cho AuraCrypt.
Cung cấp các function để quản lý danh sách categories và xử lý việc chuyển entry
khi category bị xóa.
"""

class CategoryManager:
    """Class quản lý categories."""

    DEFAULT_CATEGORY = "Uncategorized"
    DEFAULT_CATEGORIES = ["Personal", "Work", "Social", "Finance", "Shopping", "Entertainment"]

    @staticmethod
    def get_categories_from_entries(entries: list[dict]) -> list[str]:
        """
        Trích xuất danh sách các categories từ entries và sắp xếp alphabetically.

        Args:
            entries: Danh sách các entries

        Returns:
            Danh sách categories được sắp xếp, bao gồm DEFAULT_CATEGORY
        """
        categories = set()

        # Lấy tất cả categories từ entries
        for entry in entries:
            category = entry.get('category', '').strip()
            if category:
                categories.add(category)

        # Thêm DEFAULT_CATEGORY nếu chưa có
        categories.add(CategoryManager.DEFAULT_CATEGORY)

        # Sắp xếp và trả về
        return sorted(list(categories))

    @staticmethod
    def get_predefined_categories() -> list[str]:
        """
        Lấy danh sách categories được định nghĩa sẵn.

        Returns:
            Danh sách categories mặc định
        """
        return CategoryManager.DEFAULT_CATEGORIES.copy()

    @staticmethod
    def normalize_category(category: str) -> str:
        """
        Chuẩn hóa tên category (trim và capitalize).

        Args:
            category: Tên category cần chuẩn hóa

        Returns:
            Tên category đã được chuẩn hóa
        """
        if not category or not category.strip():
            return CategoryManager.DEFAULT_CATEGORY

        # Trim và capitalize từng từ
        return ' '.join(word.capitalize() for word in category.strip().split())

    @staticmethod
    def move_entries_to_default_category(entries: list[dict], deleted_category: str) -> list[dict]:
        """
        Chuyển tất cả entries từ category bị xóa vào DEFAULT_CATEGORY.

        Args:
            entries: Danh sách entries
            deleted_category: Tên category bị xóa

        Returns:
            Danh sách entries đã được cập nhật
        """
        updated_entries = []

        for entry in entries:
            entry_copy = entry.copy()
            if entry_copy.get('category', '').strip() == deleted_category:
                entry_copy['category'] = CategoryManager.DEFAULT_CATEGORY
            updated_entries.append(entry_copy)

        return updated_entries

    @staticmethod
    def get_entries_count_by_category(entries: list[dict]) -> dict[str, int]:
        """
        Đếm số lượng entries trong mỗi category.

        Args:
            entries: Danh sách entries

        Returns:
            Dictionary với key là category name và value là số lượng entries
        """
        count = {}

        for entry in entries:
            category = entry.get('category', '').strip()
            if not category:
                category = CategoryManager.DEFAULT_CATEGORY

            count[category] = count.get(category, 0) + 1

        return count

    @staticmethod
    def validate_category_name(category_name: str) -> tuple[bool, str]:
        """
        Kiểm tra tính hợp lệ của tên category.

        Args:
            category_name: Tên category cần kiểm tra

        Returns:
            Tuple (is_valid, error_message)
        """
        if not category_name or not category_name.strip():
            return False, "Category name cannot be empty"

        normalized = CategoryManager.normalize_category(category_name)

        if len(normalized) > 50:
            return False, "Category name must be 50 characters or less"

        if normalized == CategoryManager.DEFAULT_CATEGORY:
            return False, f"'{CategoryManager.DEFAULT_CATEGORY}' is a reserved category name"

        # Kiểm tra ký tự đặc biệt (chỉ cho phép chữ cái, số, space, dash, underscore)
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', normalized):
            return False, "Category name can only contain letters, numbers, spaces, hyphens, and underscores"

        return True, ""

    @staticmethod
    def validate_category_rename(old_name: str, new_name: str, existing_categories: list[str]) -> tuple[bool, str]:
        """
        Kiểm tra tính hợp lệ khi đổi tên category.

        Args:
            old_name: Tên category hiện tại
            new_name: Tên category mới
            existing_categories: Danh sách các categories hiện có

        Returns:
            Tuple (is_valid, error_message)
        """
        # Kiểm tra category cũ có phải DEFAULT_CATEGORY không
        if old_name == CategoryManager.DEFAULT_CATEGORY:
            return False, f"Cannot rename the '{CategoryManager.DEFAULT_CATEGORY}' category"

        # Kiểm tra tính hợp lệ của tên mới
        is_valid, error_message = CategoryManager.validate_category_name(new_name)
        if not is_valid:
            return False, error_message

        normalized_new = CategoryManager.normalize_category(new_name)
        normalized_old = CategoryManager.normalize_category(old_name)

        # Nếu tên mới giống tên cũ thì không cần đổi
        if normalized_new == normalized_old:
            return False, "New name is the same as current name"

        # Kiểm tra tên mới đã tồn tại chưa
        if normalized_new in existing_categories:
            return False, "Category with this name already exists"

        return True, ""

    @staticmethod
    def rename_category_in_entries(entries: list[dict], old_category: str, new_category: str) -> list[dict]:
        """
        Đổi tên category trong tất cả entries có category cũ.

        Args:
            entries: Danh sách entries
            old_category: Tên category cũ
            new_category: Tên category mới

        Returns:
            Danh sách entries đã được cập nhật
        """
        updated_entries = []

        for entry in entries:
            entry_copy = entry.copy()
            if entry_copy.get('category', '').strip() == old_category:
                entry_copy['category'] = new_category
            updated_entries.append(entry_copy)

        return updated_entries
