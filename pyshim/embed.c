#include <Python.h>
#include <stdint.h>
extern char *hb_core_request(const char *);
extern void hb_core_free(char *);
extern void hb_set_frozen(void);
extern void hb_seed_state(uint64_t, uint32_t *);
static PyObject *seed_state(PyObject *self, PyObject *args) {
    (void)self;
    unsigned long long seed;
    if (!PyArg_ParseTuple(args, "K", &seed)) return NULL;
    uint32_t words[624];
    hb_seed_state((uint64_t)seed, words);
    PyObject *state = PyTuple_New(625);
    if (!state) return NULL;
    for (int i = 0; i <= 624; ++i) {
        PyObject *word = PyLong_FromUnsignedLong(i == 624 ? 624 : words[i]);
        if (!word) { Py_DECREF(state); return NULL; }
        PyTuple_SET_ITEM(state, i, word);
    }
    return state;
}
static PyObject *request(PyObject *self, PyObject *args) {
    (void)self;
    const char *input;
    if (!PyArg_ParseTuple(args, "s", &input)) return NULL;
    char *output = hb_core_request(input);
    PyObject *result = PyUnicode_FromString(output);
    hb_core_free(output);
    return result;
}
static PyMethodDef methods[] = {{"request", request, METH_VARARGS, "Internal scene-core JSON bridge."}, {"seed_state", seed_state, METH_VARARGS, "Internal deterministic seed state."}, {NULL, NULL, 0, NULL}};
static struct PyModuleDef module = {PyModuleDef_HEAD_INIT, "_hb", NULL, -1, methods, NULL, NULL, NULL, NULL};
static PyObject *init_hb(void) { return PyModule_Create(&module); }
int hb_python_init(void) {
    hb_set_frozen();
    static int registered = 0;
    if (!registered) {
        if (PyImport_AppendInittab("_hb", init_hb) == -1) return -1;
        registered = 1;
    }
    PyConfig config;
    PyConfig_InitIsolatedConfig(&config);
    config.site_import = 0;
    config.write_bytecode = 0;
    config.module_search_paths_set = 1;
    config.install_signal_handlers = 0;
    config.use_hash_seed = 1;
    config.hash_seed = 0;
    PyStatus status = Py_InitializeFromConfig(&config);
    PyConfig_Clear(&config);
    if (PyStatus_Exception(status)) { fprintf(stderr, "%s\n", status.err_msg); return -1; }
    return 0;
}
int hb_python_exec(const char *source) { return PyRun_SimpleString(source); }
int hb_python_finish(void) { return Py_FinalizeEx(); }
