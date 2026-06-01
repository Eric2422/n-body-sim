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
   [5]
