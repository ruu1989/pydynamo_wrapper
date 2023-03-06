class NoSKFoundException(Exception):
    message = 'No attribute is defined with \'sk\' flag in attribute block'


class MultipleSKsFoundException(Exception):
    message = 'Multiple attributes defined with \'sk\' flag in attribute block'
