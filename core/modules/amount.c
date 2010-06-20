#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "structmember.h"

#ifdef _MSC_VER
typedef __int64 int64_t;
double round(double x) { return floor(x + 0.5); }
int rint(double x) { return (int)round(x); }
#endif

typedef struct {
    PyObject_HEAD
    int64_t ival; /* Value shifted by currency's exponent */
    PyObject *currency; /* a Currency instance */
    PyObject *rval; /* Real value, as a python float instance */
} Amount;

static PyTypeObject Amount_Type; /* Forward declaration */

/* Utility funcs */

static int64_t
get_amount_ival(PyObject *amount)
{
    /* Returns amount's ival if it's an amount, or 0 if it's an int with a value of 0.
       Call check_amount() before using this.
    */
    if (PyObject_TypeCheck(amount, &Amount_Type)) {
        return ((Amount *)amount)->ival;
    }
    else { /* it's an int and it *has* to be 0 */
        return 0;
    }
}

static int
get_currency_exponent(PyObject *currency)
{
    /* Returns -1 if there's a problem. */
    PyObject *tmp;
    int r;
    
    tmp = PyObject_GetAttrString(currency, "exponent");
    if (tmp == NULL) {
        return -1;
    }
    r = PyInt_AsLong(tmp);
    Py_DECREF(tmp);
    return r;
}

static int
amounts_are_compatible(PyObject *a, PyObject *b)
{
    /* a and b are either Amount instances or 0 */
    PyObject *tmp1, *tmp2;
    int64_t aval, bval;
    
    aval = get_amount_ival(a);
    bval = get_amount_ival(b);
    
    if (aval && bval) {
        /* None of the values are zero, we must make sure the currencies are the same */
        tmp1 = ((Amount *)a)->currency;
        tmp2 = ((Amount *)b)->currency;
        return PyObject_RichCompareBool(tmp1, tmp2, Py_EQ);
    }
    else {
        return 1;
    }
}

static int
check_amount(PyObject *o)
{
    /* Returns true if o is an amount and false otherwise.
       A valid amount is either an Amount instance or an int instance with the value of 0.
    */
    if (PyObject_TypeCheck(o, &Amount_Type)) {
        return 1;
    }
    if (!PyInt_Check(o)) {
        return 0;
    }
    return PyInt_AS_LONG(o) == 0;
}

static int
check_amounts(PyObject *a, PyObject *b, int seterr)
{
    /* Verify that a and b are amounts and compatible together and returns true or false.
       if seterr is true, an appropriate error is set.
    */
    if (!check_amount(a) || !check_amount(b)) {
        if (seterr) {
            PyErr_SetString(PyExc_TypeError, "Amounts can only be compared with other amounts or zero.");
        }
        return 0;
    }
    
    if (!amounts_are_compatible(a, b)) {
        if (seterr) {
            PyErr_SetString(PyExc_ValueError, "Amounts of different currencies can't be compared.");
        }
        return 0;
    }
    
    return 1;
}

static PyObject *
create_amount(int64_t ival, PyObject *currency)
{
    /* Create a new amount in a way that is faster than the normal init */
    Amount *r;
    double dtmp;
    int exponent;
    
    r = (Amount *)Amount_Type.tp_alloc(&Amount_Type, 0);
    r->ival = ival;
    r->currency = currency;
    Py_INCREF(currency);
    exponent = get_currency_exponent(currency);
    dtmp = (double)ival / pow(10, exponent);
    r->rval = PyFloat_FromDouble(dtmp);
    if (r->rval == NULL) {
        return NULL;
    }
    return (PyObject *)r;
}

/* Methods */

static void
Amount_dealloc(Amount *self)
{
    Py_XDECREF(self->currency);
    Py_XDECREF(self->rval);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Amount_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Amount *self;
    
    self = (Amount *)type->tp_alloc(type, 0);
    if (self == NULL) {
        return NULL;
    }
    self->currency = Py_None;
    Py_INCREF(self->currency);
    self->rval = PyFloat_FromDouble(0);
    if (self->rval == NULL) {
        Py_DECREF(self);
        return NULL;
    }
    self->ival = 0;
    
    return (PyObject *)self;
}

static int
Amount_init(Amount *self, PyObject *args, PyObject *kwds)
{
    PyObject *amount, *currency, *tmp;
    int exponent;
    double dtmp;
    
    static char *kwlist[] = {"amount", "currency", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|OO", kwlist, &amount, &currency)) {
        return -1;
    }
    
    if (currency) {
        tmp = self->currency;
        Py_INCREF(currency);
        self->currency = currency;
        Py_XDECREF(tmp);
    }
    
    exponent = get_currency_exponent(self->currency);
    if (exponent == -1) {
        return -1;
    }
    
    if (amount) {
        dtmp = PyFloat_AsDouble(amount);
        if (dtmp == -1 && PyErr_Occurred()) {
            return -1;
        }
        self->ival = round(dtmp * pow(10, exponent));
        tmp = self->rval;
        Py_INCREF(amount);
        self->rval = amount;
        Py_XDECREF(tmp);
    }

    return 0;
}

static int
Amount_traverse(Amount *self, visitproc visit, void *arg)
{
    Py_VISIT(self->rval);
    Py_VISIT(self->currency);
    return 0;
}

static int
Amount_clear(Amount *self)
{
    Py_CLEAR(self->rval);
    Py_CLEAR(self->currency);
    return 0;
}

static PyObject *
Amount_copy(PyObject *self)
{
    return create_amount(((Amount *)self)->ival, ((Amount *)self)->currency);
}

static PyObject *
Amount_deepcopy(PyObject *self, PyObject *args, PyObject *kwds)
{
    return Amount_copy(self);
}

static PyObject *
Amount_repr(Amount *self)
{
    int exponent;
    PyObject *r, *fmt, *args;
    
    exponent = get_currency_exponent(self->currency);
    args = Py_BuildValue("(iOO)", exponent, self->rval, self->currency);
    fmt = PyString_FromString("Amount(%.*f, %r)");
    r = PyString_Format(fmt, args);
    Py_DECREF(fmt);
    Py_DECREF(args);
    return r;
}

static PyObject *
Amount_richcompare(PyObject *a, PyObject *b, int op)
{
    int64_t aval, bval;
    int r, is_eq_op;
    
    is_eq_op = (op == Py_EQ) || (op == Py_NE);
    
    if (!check_amounts(a, b, !is_eq_op)) {
        if (op == Py_EQ) {
            Py_RETURN_FALSE;
        }
        else if (op == Py_NE) {
            Py_RETURN_TRUE;
        }
        else {
            return NULL; // An error has been set already
        }
    }
    
    /* The comparison is valid, do it */
    r = 0;
    aval = get_amount_ival(a);
    bval = get_amount_ival(b);
    switch (op) {
        case Py_LT: r = aval < bval; break;
        case Py_LE: r = aval <= bval; break;
        case Py_EQ: r = aval == bval; break;
        case Py_NE: r = aval != bval; break;
        case Py_GT: r = aval > bval; break;
        case Py_GE: r = aval >= bval; break;
    }
    if (r) {
        Py_RETURN_TRUE;
    }
    else {
        Py_RETURN_FALSE;
    }
}

static PyObject *
Amount_neg(Amount* self)
{
    return create_amount(-self->ival, self->currency);
}

static int
Amount_nonzero(Amount *self)
{
    return self->ival != 0;
}

static PyObject *
Amount_abs(Amount* self)
{
    if (self->ival >= 0) {
        Py_INCREF(self);
        return (PyObject *)self;
    }
    else {
        return Amount_neg(self);
    }
}

static PyObject *
Amount_float(Amount* self)
{
    return PyNumber_Float(self->rval);
}

static PyObject *
Amount_add(PyObject *a, PyObject *b)
{
    int64_t aval, bval;
    PyObject *currency;
    
    if (!check_amounts(a, b, 1)) {
        return NULL;
    }
    aval = get_amount_ival(a);
    bval = get_amount_ival(b);
    if (aval && bval) {
        currency = ((Amount *)a)->currency;
        return create_amount(aval + bval, currency);
    }
    else if (aval) {
        /* b is 0, return a */
        Py_INCREF(a);
        return a;
    }
    else {
        /* whether b is 0 or not, we return it */
        Py_INCREF(b);
        return b;
    }
}

static PyObject *
Amount_sub(PyObject *a, PyObject *b)
{
    int64_t aval, bval;
    PyObject *currency;
    
    if (!check_amounts(a, b, 1)) {
        return NULL;
    }
    aval = get_amount_ival(a);
    bval = get_amount_ival(b);
    if (aval && bval) {
        currency = ((Amount *)a)->currency;
        return create_amount(aval - bval, currency);
    }
    else if (aval) {
        /* b is 0, return a */
        Py_INCREF(a);
        return a;
    }
    else if (bval) {
        /* a is 0 but not b, return -b */
        return Amount_neg((Amount *)b);
    }
    else {
        /* both a and b are 0, return any */
        Py_INCREF(a);
        return a;
    }
}

static PyObject *
Amount_mul(PyObject *a, PyObject *b)
{
    double dval;
    int64_t ival;
    
    /* first, for simplicity, handle reverse op */
    if (!PyObject_TypeCheck(a, &Amount_Type) && PyObject_TypeCheck(b, &Amount_Type)) {
        return Amount_mul(b, a);
    }
    /* it is assumed that a is an amount */
    if (PyObject_TypeCheck(b, &Amount_Type)) {
        PyErr_SetString(PyExc_TypeError, "Can't multiply two amounts together");
        return NULL;
    }
    
    dval = PyFloat_AsDouble(b);
    if (dval == -1 && PyErr_Occurred()) {
        return NULL;
    }
    
    if (dval == 0) {
        return PyInt_FromLong(0);
    }
    
    ival = rint(((Amount *)a)->ival * dval);
    return create_amount(ival, ((Amount *)a)->currency);
}

static PyObject *
Amount_div(PyObject *a, PyObject *b)
{
    double dval;
    int64_t ival;
    
    if (!PyObject_TypeCheck(a, &Amount_Type)) {
        PyErr_SetString(PyExc_TypeError, "An amount can't divide something else.");
        return NULL;
    }
    
    if (PyObject_TypeCheck(b, &Amount_Type)) {
        if (!amounts_are_compatible(a, b)) {
            PyErr_SetString(PyExc_ValueError, "Amounts of different currency can't be divided.");
            return NULL;
        }
        // Return both rval divided together
        return PyNumber_TrueDivide(((Amount *)a)->rval, ((Amount *)b)->rval);
    }
    else {
        dval = PyFloat_AsDouble(b);
        if (dval == -1 && PyErr_Occurred()) {
            return NULL;
        }
    }
    
    if (dval == 0) {
        PyErr_SetString(PyExc_ZeroDivisionError, "");
        return NULL;
    }
    
    ival = rint(((Amount *)a)->ival / dval);
    return create_amount(ival, ((Amount *)a)->currency);
}

static PyObject *
Amount_getcurrency(Amount *self)
{
    Py_INCREF(self->currency);
    return self->currency;
}

static PyObject *
Amount_getvalue(Amount *self)
{
    Py_INCREF(self->rval);
    return self->rval;
}

static PyMemberDef Amount_members[] = {
    {NULL}  /* Sentinel */
};

/* We need both __copy__ and __deepcopy__ methods for amounts to behave correctly in undo_test. */

static PyMethodDef Amount_methods[] = {
    {"__copy__", (PyCFunction)Amount_copy, METH_NOARGS, ""},
    {"__deepcopy__", (PyCFunction)Amount_deepcopy, METH_VARARGS, ""},
    {NULL}  /* Sentinel */
};

static PyGetSetDef Amount_getseters[] = {
    {"currency", (getter)Amount_getcurrency, NULL, "currency", NULL},
    {"value", (getter)Amount_getvalue, NULL, "value", NULL},
    {NULL}  /* Sentinel */
};

static PyNumberMethods Amount_as_number = {
	(binaryfunc)Amount_add, /* nb_add */
	(binaryfunc)Amount_sub, /* nb_subtract */
	(binaryfunc)Amount_mul, /* nb_multiply */
	(binaryfunc)Amount_div, /* nb_divide */
	0, /* nb_remainder */
	0, /* nb_divmod */
	0, /* nb_power */
	(unaryfunc)Amount_neg, /* nb_negative */
	0, /* nb_positive */
	(unaryfunc)Amount_abs, /* nb_absolute */
	(inquiry)Amount_nonzero, /* nb_nonzero */
	0,					/*nb_invert*/
	0,					/*nb_lshift*/
	0,					/*nb_rshift*/
	0,					/*nb_and*/
	0,					/*nb_xor*/
	0,					/*nb_or*/
	0,					/*nb_coerce*/
	0,					/*nb_int*/
	0,					/*nb_long*/
	(unaryfunc)Amount_float, /*nb_float*/
	0,					/*nb_oct*/
	0, 					/*nb_hex*/
	0,					/*nb_inplace_add*/
	0,					/*nb_inplace_subtract*/
	0,					/*nb_inplace_multiply*/
	0,					/*nb_inplace_divide*/
	0,					/*nb_inplace_remainder*/
	0,					/*nb_inplace_power*/
	0,					/*nb_inplace_lshift*/
	0,					/*nb_inplace_rshift*/
	0,					/*nb_inplace_and*/
	0,					/*nb_inplace_xor*/
	0,					/*nb_inplace_or*/
	0,  				/* nb_floor_divide */
	0,					/* nb_true_divide */
	0,					/* nb_inplace_floor_divide */
	0,					/* nb_inplace_true_divide */
};

static PyTypeObject Amount_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_amount.Amount",             /*tp_name*/
    sizeof(Amount),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Amount_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc)Amount_repr,     /*tp_repr*/
    &Amount_as_number,          /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_RICHCOMPARE | Py_TPFLAGS_CHECKTYPES, /*tp_flags*/
    "Amount object",           /* tp_doc */
    (traverseproc)Amount_traverse,       /* tp_traverse */
    (inquiry)Amount_clear,            /* tp_clear */
    (richcmpfunc)Amount_richcompare, /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    Amount_methods,             /* tp_methods */
    Amount_members,             /* tp_members */
    Amount_getseters,          /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Amount_init,      /* tp_init */
    0,                         /* tp_alloc */
    Amount_new,                 /* tp_new */
};

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

PyMODINIT_FUNC
init_amount(void) 
{
    PyObject *m;

    if (PyType_Ready(&Amount_Type) < 0) {
        return;
    }
    
    m = Py_InitModule3("_amount", module_methods, "Home of the Amount class.");

    if (m == NULL)
      return;
    
    Py_INCREF(&Amount_Type);
    PyModule_AddObject(m, "Amount", (PyObject *)&Amount_Type);
}