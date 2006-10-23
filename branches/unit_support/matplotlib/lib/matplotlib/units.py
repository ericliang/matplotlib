
class UnitsTagInterface:
    """
       This interface describes the expected protocol for types implementing
       values tagged with measurement units.

       In addition for an implementation that represents values along with
       an associated measurement unit, matplotlib needs a consistent 
       mechanism for passing unit types.  To matplotlib, units are 
       merely identifiers, and the actual objects can be of any 
       Python type, as long as the implementation of convert_to()
       handles that Python type.  So, units could be unique strings
       or specialized objects, depending on the implementation of the
       value class.

       For custom TickLocator and TickFormatter instances, one must define
       a function that returns locators and formatter pairs corresponding
       to a unit.  The function should return a tuple containing a major
       locator/formatter object and a minor locator/formatter object.
       Example:
           def simple_locator_map(unit_object):
               'returns (major locator, minor locator) tuple for unit'
               return (AutoLocator(), NullLocator())

       Once defined, the function must be passed to the current Axes
       object in one of two ways.

       First, the implementations of get_unit_to_[formatter|locator]_map()
       can return this function.

       Second, default maps can be specified using the static methods
       in the Axes class, set_default_unit_to_[locator|formatter]_map().

       When determining the locator/formatter, the first valid
       locator/formatter pair is used.  All supplied data is queried
       for locator/formatter functions, and the default map is checked
       only when a check of the data results in no valid locator/formatter
       pairs.

       Lastly, duplicate functions (duplicate Python objects) are not
       checked multiple times.  Thus, whenever possible, returning the
       same Python object as the locator/formatter function may improve
       efficiency.
    """
    def convert_to(self, unit):
        """Converts the existing units object to the specified units object.
           Parameters:
             unit - unit of the desired type
           Returns:
             object converted to the requested units (should be of a type
             that supports this interface)
        """
        raise NotImplemented
    def get_value(self):
        """Returns the quantities stripped of unit.
        """
        raise NotImplemented
    def convert_to_value(self, unit):
        """
           Converts the existing units object to the specified units
           object and strips the target unit, leaving the unit-less
           values.  If convert_to() and convert_to_value() are
           both implemented, val.convert_to_value() should be equivalent
           to val.convert_to().get_value().
           Parameters:
             unit - unit of the desired type
           Returns:
             values converted to the requested units
        """
        raise NotImplemented
    def get_unit_to_locator_map(self):
        """
           If a custom locators are desired, this method should return
           a function with the profile
             fn(unit) => (<major locator>, <minor locator>)
           In the absence of a valid return, the default locators
           are used.
        """
        return None
    def get_unit_to_formatter_map(self):
        """
           If a custom formatters are desired, this method should return
           a function with the profile
             fn(unit) => (<major formatter>, <minor formatter>)
           In the absence of a valid return, the default formatters
           are used.
        """
        return None
           
