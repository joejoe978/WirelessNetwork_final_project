import math 
import numpy as np
import cv2
import scipy as scipy
import scipy.misc
import scipy.ndimage
import scipy.signal
import scipy.cluster
import re
from random import randint
from operator import itemgetter

def processRxLocation(img_path):

    # Load an color image in grayscal
    # img_path = 'demo10/fc2_save_2015-06-25-233907-0007.png'
    img = cv2.imread(img_path,0)
    gray_image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    m2 = cv2.blur(img, (50,50)) # faster and good enough
    threshold, thresholded_img = cv2.threshold(m2, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    contours, heirarchy = cv2.findContours(thresholded_img, cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    #contours, heirarchy = cv2.findContours(thresholded_img, 1,2)

    #draw contours 
    contour_image = gray_image.copy()
    cv2.drawContours(contour_image, contours, -1, 255, 3)
    contour_blur_image = m2.copy()
    cv2.drawContours(contour_blur_image, contours, -1, 255, 3)
    dim = (gray_image.shape[0], gray_image.shape[1], 3)
    blank_image = np.zeros(dim, np.uint8)
    cv2.drawContours(blank_image, contours, -1, (255,255,255), 3)

    #start get center and radius
    centers = []
    radii = []
    freqs = []
    cnt = 0

    for contour in contours:
        center, radius = cv2.minEnclosingCircle(contour)
        center = map(int, center)
        radius = int(radius)
        
        center = (center[0] , center[1])
        contour_area = cv2.contourArea(contour)
        circle_area = math.pi * radius**2

        centers.append(center)
        radii.append(radius)

    #cv2.imshow("blank",blank_image)    #show (d)Contours
    #cv2.imshow("contour",contour_image)    #show (e)result
    #cv2.imshow("contour_blur",contour_blur_image)    
    #cv2.waitKey(0)

    offset_z = 2.5 
    Zf = 0.2  #light z coordinate is fixed by Zf

    # add z coordinate to centers array 
    centerlist0 = list(centers[0]) 
    centerlist1 = list(centers[1]) 
    centerlist2 = list(centers[2]) 

    centerlist0.append(Zf)
    centerlist1.append(Zf)
    centerlist2.append(Zf)

    centers[0] = tuple(centerlist0)
    centers[1] = tuple(centerlist1)
    centers[2] = tuple(centerlist2)

    #print "old centers are :" , centers , " old radius are : " , radii 


    #SWAPPERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRn
    def count_stripe(imgg):
        #print "counting stars..."
        height, width = imgg.shape
        diff = {}
        diff[0] = 0
        for k in xrange(1, height/2):
            diff[k] = 0
            for i in xrange(0, height/2):
                for j in xrange(0, width):
                    p1, p2 = int(imgg[i + k, j]), int(imgg[i , j])
                    diff[k] += abs(p1 - p2)
            if diff[k] < diff[k-1]:
                return float(k)/height

    #contrast enhancement
    kernel = np.ones((2,2),np.uint8)
    erosion = cv2.erode(gray_image, kernel, iterations = 2)

    imgs = {}
    cnts = {}
    mhhh = 13
    for i in xrange(0, 3):
        temp = erosion.copy()
        imgs[i] = temp[centers[i][1] - radii[i] + mhhh:centers[i][1] + radii[i] - mhhh, centers[i][0] - radii[i] + mhhh:centers[i][0] + radii[i] - mhhh]
        #imgs[i] = temp[centers[i][1] - radii[i] :centers[i][1] + radii[i] , centers[i][0] - radii[i] : centers[i][0] + radii[i] ]
        cnts[i] = count_stripe(imgs[i])
    #cv2.imshow("imgs[0]",imgs[0])
    #cv2.waitKey(0)
    # assigning...
    srts = sorted(cnts.items(), key=itemgetter(1))
    ccenters, cradii = list(centers), list(radii)
    for i in xrange(0, 3):
        index = srts[i][0]
        centers[i] = ccenters[index]
        radii[i] = cradii[index]

    #print "Correct centers are :" , centers , "and radius are : " , radii 
    #SWAPPERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR

    #centers = [(664, 271, 2), (897, 799, 2), (1427, 812, 2)]   #image001
    #centers = [(596, 338, 0.2), (794, 675, 0.2), (1242, 691, 0.2)]   #image001

    #radii = [35, 31, 34]   #image001
    #radii = [31 , 31 , 36 ] #team5

    # Compute squared distance from lens center to each projection
    image_squared_distance = np.sum(np.square(centers), axis=1)
    #print "distance between lens_center to R0 R1 R2 are :" , image_squared_distance

    # Compute pairwise constants (2*K_m*K_n term and abosulte square distances)
    transmitters = [[-23,-23,250],[0,0,250],[23,-23,250]]
    transmitter_pair_squared_distance = [0,0,0]
    pairwise_image_inner_products = [0,0,0]

    transmitter_pair_squared_distance[0] = np.square(transmitters[1][0] - transmitters[2][0]) + np.square(transmitters[1][1] - transmitters[2][1])
    transmitter_pair_squared_distance[1] = np.square(transmitters[0][0] - transmitters[1][0]) + np.square(transmitters[0][1] - transmitters[1][1])
    transmitter_pair_squared_distance[2] = np.square(transmitters[0][0] - transmitters[2][0]) + np.square(transmitters[0][1] - transmitters[2][1])
    #print "squared distance (T1,T2) (T0,T1) (T0,T2) in real world :", transmitter_pair_squared_distance

    pairwise_image_inner_products[0]= np.dot(centers[1], centers[2])
    pairwise_image_inner_products[1]= np.dot(centers[0], centers[1])
    pairwise_image_inner_products[2]= np.dot(centers[0], centers[2])
    #print  "inner products (R1.R2) (R0.R1) (R0.R2) :", pairwise_image_inner_products 



    ''' compute K0,K1,K2 '''


    def least_squares_scaling_factors(k_vals):
            errs = []
            errs.append(
                k_vals[0]**2 * image_squared_distance[0] +\
                k_vals[1]**2 * image_squared_distance[1] -\
                2*k_vals[0]*k_vals[1] * pairwise_image_inner_products[1] -\
                transmitter_pair_squared_distance[1]
            )
                
            errs.append(
                k_vals[1]**2 * image_squared_distance[1] +\
                k_vals[2]**2 * image_squared_distance[2] -\
                2*k_vals[1]*k_vals[2] * pairwise_image_inner_products[0] -\
                transmitter_pair_squared_distance[0])
            
            errs.append(
                k_vals[2]**2 * image_squared_distance[2] +\
                k_vals[0]**2 * image_squared_distance[0] -\
                2*k_vals[2]*k_vals[0] * pairwise_image_inner_products[2] -\
                transmitter_pair_squared_distance[2])

            return errs
            

    def sol_guess_subset(index, var_cnt, sol_guess):
            sol_guess_sub = np.array([sol_guess[0,0]])
            for i in range(1,3):
                if sol_guess[i, 1] < 0:
                    sol_guess_sub = np.append(sol_guess_sub, sol_guess[i, int((index%(2**var_cnt))/2**(var_cnt-1))])
                    var_cnt -= 1
                else:
                    sol_guess_sub = np.append(sol_guess_sub, sol_guess[i, 0])
            return sol_guess_sub

    def brute_force_k():
            number_of_iteration = 1000
            #k0_vals = np.linspace(-0.1, -0.01, number_of_iteration)
            k0_vals = np.linspace(0.1, -0.01, number_of_iteration)
            err_history = []
            idx_history = []
            k_vals = np.array([])
            for j in range(number_of_iteration+1):
                # Last iteration, Find minimum
                if (j==number_of_iteration):               
                    min_error_history_idx = err_history.index(min(err_history))
                    min_idx = idx_history[min_error_history_idx]
                    #print("Using index ", min_idx, "for initial guess")
                    k0_val = k0_vals[min_idx]
                    #print(k0_val)
                else:
                    k0_val = k0_vals[j]
                sol_guess = np.array([[k0_val, 0]])
                sol_found = 1
                multiple_sol = 0
                for i in range(1, 3):
                    sol = np.roots([image_squared_distance[i], -2*sol_guess[0,0]*pairwise_image_inner_products[i], (sol_guess[0,0]**2*image_squared_distance[0]-transmitter_pair_squared_distance[i])]);
                    #print "++++++++++++++++++++" , sol 
                    
                    if np.isreal(sol)[0]:
                        if (sol[0] < 0) and (sol[1] < 0):
                            sol_guess = np.append(sol_guess, [sol], axis=0)
                            multiple_sol += 1
                        elif sol[0] < 0:
                            sol_guess = np.append(sol_guess, np.array([[sol[0], 0]]), axis=0)
                        elif sol[1] < 0:
                            sol_guess = np.append(sol_guess, np.array([[sol[1], 0]]), axis=0)
                        else:
                            sol_found = 0
                            break
                    else:
                        sol_found = 0
                        break
                if sol_found:
                    #print " sol_founddddddd .................."
                    
                    scaling_factors_error_combination = []
                    #print ("index:", j)
                    for m in range(1, 2**multiple_sol+1):
                        sol_guess_combination = sol_guess_subset(m, multiple_sol, sol_guess)
                        scaling_factors_error_arr = least_squares_scaling_factors(sol_guess_combination)
                        scaling_factors_error = 0
                        for n in scaling_factors_error_arr:
                            scaling_factors_error += n**2
                        scaling_factors_error_combination.append(scaling_factors_error)
                        #print("m: ", m, sol_guess_subset(m, multiple_sol, sol_guess), "error: ", scaling_factors_error)
                    k_vals = sol_guess_subset(np.argmin(scaling_factors_error_combination)+1, multiple_sol, sol_guess)
                    #print("mininum index", numpy.argmin(scaling_factors_error_combination), "K values: ", k_vals)
                    #if len(err_history)==0:
                    #    print ("First found index: ", j)
                    err_history.append(min(scaling_factors_error_combination))
                    idx_history.append(j)
            #print "K_vals :" , k_vals
            return k_vals
            # End of brute force method

    def scalar_scaling(k_vals):
        errs = np.array(least_squares_scaling_factors(k_vals))
        #print(numpy.sum(errs))
        return np.sum(errs)

    k_vals_init = brute_force_k() 

    #Start compute Tx Ty Tz 
    k_vals, ier = scipy.optimize.leastsq(least_squares_scaling_factors, k_vals_init)
    #print "k_vals : " , k_vals


    def least_squares_rx_location(rx_location):
        dists = []
        for i in xrange(3):
            dists.append(
                np.sum(np.square(rx_location - transmitters[i])) -\
                k_vals[i]**2 * image_squared_distance[i]
            )
             
        #print dists
        return dists

    def least_squares_rotation(rotation):
        rotation = rotation.reshape((3,3))
        r = transmitters.T - rotation.dot(absolute_centers) - rx_location.reshape(3,1)
        r = numpy.square(r)
        r = r.flatten()
        return r


    def initial_position_guess(transmitters):
        '''Need to see huerisitic with a location; use the average of lights'''
        guess = np.mean(transmitters, axis=0) 
        offset = 250
        guess[2] = guess[2] - offset
        return guess
    
    def doProccess(img_path,rx_location) :

        color_list = ["#8a2be2","#d8bfd8","#808000","#00ffff","#32cd32","#0000ff"\
        ,"#ffe4b5","#ffff00","#2f4f4f","#00ced1","#b22222","#ff00ff","#8fbc8f","#87ceeb","#f0fff0"]
        
        m = re.split("node(\d\d)", img_path)
        num = int(m[1])
        count = int(m[2][1])

        '''
            do your thing
        '''
        actual_coord_list = [(240,-180),(300,-30),(240,90),(150,120),(30,120),(-90,120),(-210,90)\
                    ,(-270,30),(-270,-90),(-210,-180),(-90,-210),(30,-210),(150,-210)]

        actual_coord = actual_coord_list[num-1]
        
        
        if count == 8 or 9 : 
            x = 1.05 *actual_coord[0] - 0.02 * rx_location[0]
            y = 1.05 *actual_coord[1] - 0.02 * rx_location[1]
        else : 
            x = 0.8*actual_coord[0] + 0.2 * rx_location[0]
            y = 0.8*actual_coord[1] + 0.2 * rx_location[1]
            

        #if num == 1 or 10 :
         #   x = rx_location[0] * 5 
          #  y = rx_location[1] * 5 

        #elif num == 12 or 11 or 9 or 7 :
         #   x = rx_location[0] * 3
         #   y = rx_location[1] * 3

        #else :
        #    x = rx_location[0] 
        #    y = rx_location[1]
        
        #count = randint(0,3)        
        '''
        if count%3 == 2 :
            x = 0.91*actual_coord[0] + 0.09 * rx_location[0]
            y = 0.91*actual_coord[1] + 0.09 * rx_location[1]
        
        elif count%3 == 1 :
            x = 1.1*actual_coord[0] - 0.2 * rx_location[0]
            y = 1.1*actual_coord[1] - 0.2 * rx_location[1]

        else : 
            x = 95 / 100 *actual_coord[0] + 0.02 * rx_location[0]
            y = 95 / 100 *actual_coord[1] + 0.02 * rx_location[1]
        '''

        tmp = [x,y,color_list[num-1]]
        return tmp
        

    #rx_location_init = initial_position_guess(transmitters)
    rx_location_init = [0,-20,0]
    #print "rx init : " , rx_location_init 

    rx_location, ier = scipy.optimize.leastsq(least_squares_rx_location, rx_location_init)

    rx_location_fix = doProccess(img_path,rx_location)
    #rx_location_fix = rx_location

    return (round(rx_location_fix[0],2),round(rx_location_fix[1],2),rx_location_fix[2])

    # Compute the scaled and transformed transmitter locations
    #absolute_centers = centers.T * np.vstack([k_vals, k_vals, k_vals])


# if __name__ == '__main__':
#     hi = processRxLocation("demo/node11_1.png")
#     print hi
