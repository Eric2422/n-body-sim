{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :show-inheritance:
   :inherited-members:

   #######
   Methods
   #######

   {% block methods %}

   .. automethod:: __init__

   {% endblock %}
.. 
   [1]

   # References

   [1] J. Leedham,
   *Automatically document all modules recursively with Sphinx autodoc*,
   <https://stackoverflow.com/a/62613202>, (2021).
