from django.template.defaultfilters import slugify


def better_slugify(text, **kwargs):
            # The SlugField has a max length of 50 characters, so we make
            # sure it doesn't exceed that.
            slug = slugify(text)[:50]

            def remove_last_word(value):
                # If there's more than one word, make sure that the slug
                # doesn't end in the middle of a word.
                if len(value.split("-")) > 1:
                    while (value[-1:] != "-") and (len(value) > 1):
                        value = value[:-1]
                    # Remove the final hyphen
                    value = value[:-1]
                return value

            remove_last_word(slug)
            return slug