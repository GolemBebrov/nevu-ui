# distutils: language = c++
# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: nonecheck=False
# cython: initializedcheck=False

from nevu_ui.fast.nvvector2.nvvector2 cimport NvVector2
from nevu_ui.fast.nvparam.nvparam cimport NvParam
from cpython.dict cimport PyDict_GetItem
from cpython.object cimport PyObject
cimport cython
from nevu_ui.fast.logic.fast_logic cimport relm_helper, rel_helper, mass_rel_helper, vec_rel_helper, get_nvrect_helper
from nevu_ui.fast.nvrect.nvrect cimport NvRect
@cython.freelist(32)
cdef class NevuCobject:
    def __cinit__(self, *args, **kwargs):
        self.coordinates = NvVector2.new(0, 0) 
        self.absolute_coordinates = NvVector2.new(0, 0)
        self.size = NvVector2.new(0, 0)
        self._resize_ratio = NvVector2.new(1, 1)
        self.params = list()
        self._blacklisted_params = list()
        self._param_links = dict()
        self._params_map = dict()

    cpdef list _get_param_names(self):
        return list(self._params_map.keys())
    
    cpdef object _find_param(self, str name):
        return self._params_map.get(name)

    cpdef void _add_param(self, str name, supported_classes, default, getter, setter, int layer):
        param = NvParam.new(name, layer, None, default, supported_classes, getter, setter)
        self.params.append(param)
        self._params_map[name] = param

    cpdef NvParam get_param_strict(self, str name):
        cdef PyObject* p_ptr = PyDict_GetItem(self._params_map, name)
        return <NvParam>p_ptr

    cpdef NvParam get_param(self, str name):
        cdef PyObject* p_ptr = PyDict_GetItem(self._params_map, name)

        if p_ptr == NULL:
            return None 
        
        return <NvParam><object>p_ptr

    cpdef object get_param_value(self, str name):
        cdef PyObject* p_ptr = PyDict_GetItem(self._params_map, name)
        if p_ptr == NULL: return None 
        cdef NvParam param = <NvParam>p_ptr
        if param.getter is not None:
            return param.getter()
        return param.value

    cpdef void set_param_value(self, str name, object new_value):
        cdef PyObject* p_ptr = PyDict_GetItem(self._params_map, name)
        if p_ptr == NULL:
            raise KeyError(f"Parameter '{name}' not found")
        cdef NvParam param = <NvParam>p_ptr
        if param.setter is not None:
            param.setter(new_value)
        else: param.value = new_value

    cpdef float relx_custom(self, float num, float min, float max):
        return rel_helper(num, self._resize_ratio.x, min, max)

    cpdef float rely_custom(self, float num, float min, float max):
        return rel_helper(num, self._resize_ratio.y, min, max)

    cpdef float relm_custom(self, float num, float min, float max):
        return relm_helper(num, self._resize_ratio.x, self._resize_ratio.y, min, max)
    
    cpdef float relx(self, float num):
        return rel_helper(num, self._resize_ratio.x, -1.0, -1.0)

    cpdef float rely(self, float num):
        return rel_helper(num, self._resize_ratio.y, -1.0, -1.0)

    cpdef float relm(self, float num):
        return relm_helper(num, self._resize_ratio.x, self._resize_ratio.y, -1.0, -1.0)

    cpdef NvVector2 rel(self, NvVector2 vec):  
        return vec_rel_helper(vec, self._resize_ratio.x, self._resize_ratio.y)

    cpdef NvRect get_nvrect(self):
        return get_nvrect_helper(self.absolute_coordinates, self._resize_ratio, self.size)

    cpdef set_coordinates(self, NvVector2 coordinates):
        if self.coordinates == coordinates:
            return
        cdef bint need_to_set = self._coordinates_setter(coordinates) #type: ignore
        if not need_to_set: return
        self.coordinates = coordinates