#include "posemath.h"         /* save as mk6skins.c */
#include "rtapi_math.h"
#include "kinematics.h"       /* decls for kinematicsForward, etc. */
#include "sincos.h"
#include "rtapi.h"		/* RTAPI realtime OS API */
#include "rtapi_app.h"		/* RTAPI realtime module decls */
#include "hal.h"

// won't let me unload this file and use another file name
// so having to keep the name the same
// to compile do: sudo bin/comp --install mk6skins.c
// todo: remove unnecessary parameters and add in precalcs


struct arcdata_data {
    hal_s32_t btrivial; 
    hal_float_t a, b, c, d, e, f, ah, tblx, armx;
    hal_float_t ac, ab; 
    hal_float_t rotrad;

    hal_float_t width; 
};



void setupconstants(struct arcdata_data *hd)
{
    hd->btrivial = 0; 
    hd->width = 1100; 

    hd->a = 745.000009;
    hd->b = 744.999987;
    hd->c = 745.000006;
    hd->d = 692.518124;
    hd->e = 695.117444;
    hd->f = 586.497957;
    hd->ah = 0.076911;
    hd->tblx = 512.306840;
    hd->armx = 387.685268;
//    hd->rotrad = (30+18.18-2.9827809887062742)/180.0*3.1415926535;
    hd->rotrad = (30+90+14.196)/180.0*3.1415926535;
}

void setupprecalcs(struct arcdata_data *hd) 
{
    //hd->ab = abanglefromtriangleabc(hd->a, hd->b, hd->c); 
    //hd->ac = abanglefromtriangleabc(hd->a, hd->c, hd->b); 
}

void jointstoxy(struct arcdata_data* hd, const double* joint, EmcPose* world)
{
    double j0home, j1home, xhome, yhome, gx, gy, j0, j1, fac; 

    if (hd->btrivial) {
        world->tran.x = joint[0]; 
        world->tran.y = joint[1]; 
        world->tran.z = joint[2];
        return; 
    } 

    j0home = hd->width/rtapi_sqrt(2.0);
    j1home = j0home; 
    xhome = hd->width/2; 
    yhome = -hd->width/2; 
    fac = -1.0; 
    
    j0 = joint[0]*fac + j0home; 
    j1 = joint[1]*fac + j1home; 
    
    gx = (j0*j0 - j1*j1 + hd->width*hd->width)/(2*hd->width); 
    gy = -rtapi_sqrt(j0*j0 - gx*gx); 
    
    world->tran.x = gx - xhome; 
    world->tran.y = gy - yhome; 
    world->tran.z = joint[2];
}

void xytojoints(struct arcdata_data* hd, const EmcPose* world, double* joint)
{
    double j0home, j1home, xhome, yhome, gx, gy, fac; 
    if (hd->btrivial) {
        joint[0] = world->tran.x;
        joint[1] = world->tran.y;
        joint[2] = world->tran.z;
        return; 
    } 

    j0home = hd->width/rtapi_sqrt(2.0);
    j1home = j0home; 
    xhome = hd->width/2; 
    yhome = -hd->width/2; 
    fac = -1.0; 

    gx = world->tran.x + xhome;
    gy = world->tran.y + yhome; 

    joint[0] = (rtapi_sqrt(gx*gx + gy*gy) - j0home)*fac;
    gx = hd->width - gx; 
    joint[1] = (rtapi_sqrt(gx*gx + gy*gy) - j1home)*fac;
    joint[2] = world->tran.z;
}


struct arcdata_data *haldata; // global object with all the parameters in it

int kinematicsForward(const double* joint, EmcPose* world, const KINEMATICS_FORWARD_FLAGS* fflags, KINEMATICS_INVERSE_FLAGS* iflags)
{
    jointstoxy(haldata, joint, world); 
    return (0);
}

int kinematicsInverse(const EmcPose* world, double* joint, const KINEMATICS_INVERSE_FLAGS* iflags, KINEMATICS_FORWARD_FLAGS* fflags)
{
    xytojoints(haldata, world, joint); 
    *fflags = 0;
    return (0);
}

int kinematicsHome(EmcPose* world, double*joint, KINEMATICS_FORWARD_FLAGS* fflags, KINEMATICS_INVERSE_FLAGS* iflags)
{
    *fflags = 0;
    *iflags = 0;
    return kinematicsForward(joint, world, fflags, iflags);
}

KINEMATICS_TYPE kinematicsType()
{
    return KINEMATICS_BOTH;
}


EXPORT_SYMBOL(kinematicsType);
EXPORT_SYMBOL(kinematicsForward);
EXPORT_SYMBOL(kinematicsInverse);

MODULE_LICENSE("GPL");

#define VTVERSION VTKINEMATICS_VERSION1

static vtkins_t vtk = {
    .kinematicsForward = kinematicsForward,
    .kinematicsInverse  = kinematicsInverse,
    // .kinematicsHome = kinematicsHome,
    .kinematicsType = kinematicsType
};


int comp_id, vtable_id;
const char *name = "mk6skins";

int rtapi_app_main(void) {
    comp_id = hal_init(name);
    if(comp_id < 0) {
        return comp_id;
    }

    vtable_id = hal_export_vtable(name, VTVERSION, &vtk, comp_id);

    if(vtable_id < 0) {
        rtapi_print_msg(RTAPI_MSG_ERR,
                        "%s: ERROR: hal_export_vtable(%s,%d,%p) failed: %d\n",
                        name, name, VTVERSION, &vtk, vtable_id );
        return -ENOENT;
    }
        
    haldata = hal_malloc(sizeof(struct arcdata_data));
    setupconstants(haldata); 
    setupprecalcs(haldata); // should be called in case a value is changed from the hal_param system below

    if (hal_param_s32_new("kins-btrivial", HAL_RW, &(haldata->btrivial), comp_id) < 0){
        rtapi_print("failed to make pin");
        return -EINVAL;
    }
    if (hal_param_float_new("kins-rotrad", HAL_RW, &(haldata->rotrad), comp_id) < 0){
        rtapi_print("failed to make pin");
        return -EINVAL;
    }
    if (hal_param_float_new("kins-a", HAL_RW, &(haldata->a), comp_id) < 0){
        rtapi_print("failed to make pin");
        return -EINVAL;
    }
    if (hal_param_float_new("kins-b", HAL_RW, &(haldata->b), comp_id) < 0){
        rtapi_print("failed to make pin");
        return -EINVAL;
    }
    if (hal_param_float_new("kins-c", HAL_RW, &(haldata->c), comp_id) < 0){
        rtapi_print("failed to make pin");
        return -EINVAL;
    }
    if (hal_param_float_new("kins-d", HAL_RW, &(haldata->d), comp_id) < 0){
        rtapi_print("failed to make pin");
        return -EINVAL;
    }
    if (hal_param_float_new("kins-e", HAL_RW, &(haldata->e), comp_id) < 0){
        rtapi_print("failed to make pin");
        return -EINVAL;
    }
    if (hal_param_float_new("kins-f", HAL_RW, &(haldata->f), comp_id) < 0){
        rtapi_print("failed to make pin");
        return -EINVAL;
    }
    if (hal_param_float_new("kins-ab", HAL_RW, &(haldata->ab), comp_id) < 0){
        rtapi_print("failed to make pin");
        return -EINVAL;
    }
    if (hal_param_float_new("kins-ac", HAL_RW, &(haldata->ac), comp_id) < 0){
        rtapi_print("failed to make pin");
        return -EINVAL;
    }
    if (hal_param_float_new("kins-ah", HAL_RW, &(haldata->ah), comp_id) < 0){
        rtapi_print("failed to make pin");
        return -EINVAL;
    }
    if (hal_param_float_new("kins-tblx", HAL_RW, &(haldata->tblx), comp_id) < 0){
        rtapi_print("failed to make pin");
        return -EINVAL;
    }
    if (hal_param_float_new("kins-armx", HAL_RW, &(haldata->armx), comp_id) < 0){
        rtapi_print("failed to make pin");
        return -EINVAL;
    }
    hal_ready(comp_id);
    return 0;
}

void rtapi_app_exit(void) { 
    hal_remove_vtable(vtable_id);
    hal_exit(comp_id); 
}
