def get_page(items, page, page_size):
    """
    Return items for the given page number (1-indexed).
      Page 1 → items[0 : page_size]
      Page 2 → items[page_size : 2*page_size]
      ...
    """
    start = page * page_size  # calculate slice start
    end = start + page_size
    return items[start:end]
