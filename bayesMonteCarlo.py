import sys
import random
import numpy as np
import cv2 as cv

MAP_FILE = "examples/r01/cape_python.png"
SA1_CORNERS = (130, 265, 180, 315)# (LG X,LG Y, PD X, PD Y)
SA2_CORNERS = (80, 255, 130, 305)# (LG X,LG Y, PD X, PD Y)
SA3_CORNERS = (105, 205, 155, 255)# (LG X,LG Y, PD X, PD Y)
found_double = []
found_fixed = []


class Search():


    # Bayesowska gra do symulacji misji poszukiwawczo-ratunkowych
    # z trzema obszarami poszukiwań
    def __init__(self,name):
        self.name = name
        self.img = cv.imread(MAP_FILE, cv.IMREAD_COLOR)
        if self.img is None:
            print("Nie można załadować pliku z mapą {}.".format(MAP_FILE),file=sys.stderr)
            sys.exit(1)
        #lokalne współrzędne względem obszaru poszukiwań
        self.area_actual = 0
        self.sailor_actual = [0,0]
        self.sa1 = self.img[SA1_CORNERS[1] : SA1_CORNERS[3],
                            SA1_CORNERS[0] : SA1_CORNERS[2]]
        self.sa2 = self.img[SA2_CORNERS[1]: SA2_CORNERS[3],
                            SA2_CORNERS[0]: SA2_CORNERS[2]]
        self.sa3 = self.img[SA3_CORNERS[1]: SA3_CORNERS[3],
                            SA3_CORNERS[0]: SA3_CORNERS[2]]
        while True:
            a = np.random.randint(0, high=1)
            a = np.random.normal(size=3)
            a /= a.sum()
            if a[0] < 1 and 0 < a[0]:
                if a[1] < 1 and 0 < a[1]:
                    if a[2] < 1 and 0 < a[2]:
                        break
        self.p1 = a[0]
        self.p2 = a[1]
        self.p3 = a[2]

        # self.p1 = 0.2
        # self.p2 = 0.5
        # self.p3 = 0.3

        self.sep1 = 0
        self.sep2 = 0
        self.sep3 = 0

    def draw_map(self,last_known):
        # Wyświetla mapę regionu wraz ze skalą, ostatnią
        # znaną lokalizacją oraz obszarami poszukiwań
        cv.line(self.img, (20,370), (70, 370), (0,0,0),2)
        cv.putText(self.img, '0',(8,370), cv.FONT_HERSHEY_PLAIN, 1, (0,0,0))
        cv.putText(self.img, "50 mil morskich",(71,370),cv.FONT_HERSHEY_PLAIN,1,(0,0,0))
        cv.rectangle(self.img,(SA1_CORNERS[0],SA1_CORNERS[1]),(SA1_CORNERS[2],SA1_CORNERS[3]),(0,0,0),1)
        cv.putText(self.img,"1",(SA1_CORNERS[0]+3, SA1_CORNERS[1]+15),cv.FONT_HERSHEY_PLAIN,1,(0,0,0))
        cv.rectangle(self.img, (SA2_CORNERS[0], SA2_CORNERS[1]), (SA2_CORNERS[2], SA2_CORNERS[3]), (0, 0, 0), 1)
        cv.putText(self.img, "2", (SA2_CORNERS[0] + 3, SA2_CORNERS[1] + 15), cv.FONT_HERSHEY_PLAIN, 1, (0,0,0))
        cv.rectangle(self.img, (SA3_CORNERS[0], SA3_CORNERS[1]), (SA3_CORNERS[2], SA3_CORNERS[3]), (0, 0, 0), 1)
        cv.putText(self.img, '3', (SA3_CORNERS[0] + 3, SA3_CORNERS[1] + 15), cv.FONT_HERSHEY_PLAIN, 1, (0,0,0))
        cv.putText(self.img, "+", last_known,cv.FONT_HERSHEY_PLAIN,1,(0,0,255))
        cv.putText(self.img, "+ = ostatnia znana lokalizacja",(240,355),cv.FONT_HERSHEY_PLAIN,1,(0,0,255))
        cv.putText(self.img,"* = rzeczywista lokalizacja",(242,370),cv.FONT_HERSHEY_PLAIN,1,(255,0,0))
        cv.destroyAllWindows()
        cv.imshow("Obszary do przeszukania",self.img)
        cv.moveWindow("Obszary do przeszukania",1160,10)
        cv.waitKey(500)
    def sailor_final_location(self,num_search_areas):
        # Zwraca współrzędne x i y rzeczywistej lokalizacji
        # zaginionego
        #znajduje wspolrzedne zeglarza wzlegem potablicy obszaru poszukiwań
        self.sailor_actual[0] = np.random.choice(self.sa1.shape[1],1)
        self.sailor_actual[1] = np.random.choice(self.sa1.shape[0],1)

        area = int(random.triangular(1, num_search_areas))

        if area == 1:
            x = self.sailor_actual[0] + SA1_CORNERS[0]
            y = self.sailor_actual[1] + SA1_CORNERS[1]
            self.area_actual = 1
        elif area ==2:
            x = self.sailor_actual[0] + SA2_CORNERS[0]
            y = self.sailor_actual[1] + SA2_CORNERS[1]
            self.area_actual = 2
        elif area ==3:
            x = self.sailor_actual[0] + SA3_CORNERS[0]
            y = self.sailor_actual[1] + SA3_CORNERS[1]
            self.area_actual = 3
        return x, y

    def calc_search_effectiveness(self):
        # Wyznacza wartość dziesiętną reprezentującą skuteczność
        # poszukiwań dla każdego obszaru
        self.sep1 = random.uniform(0.2, 0.9)
        self.sep2 = random.uniform(0.2,0.9)
        self.sep3 = random.uniform(0.2,0.9)

    def conduct_search(self, area_num,area_array,effectiveness_prob):
        # Zwraca wynik poszukiwań oraz listę przeszukanych
        # współrzędnych.
        local_y_range = range(area_array.shape[0])
        local_x_range = range(area_array.shape[1])
        coords = [(i,j) for i in local_x_range for j in local_y_range]
        random.shuffle(coords)
        coords = coords[:int((len(coords)* effectiveness_prob))]
        loc_actual = (self.sailor_actual[0], self.sailor_actual[1])
        if area_num == self.area_actual and loc_actual in coords:
            return f"Znaleziono w obszarze nr {area_num}", coords
        else:
            return "Nie znaleziono.", coords

    def revise_target_probe(self):
        # Aktualizowanie prawdopodobieństwa dla każdego
        # obszaru na podstawie skuteczności poszukiwań.
        denom = self.p1 * (1-self.sep1) + self.p2 * (1-self.sep2) + self.p3 * (1-self.sep3)
        self.p1 = self.p1 * (1-self.sep1)/denom
        self.p2 = self.p2 * (1-self.sep2)/denom
        self.p3 = self.p3 * (1-self.sep3)/denom

    def choice_maker_double(self):
        if self.p1 > self.p2 and self.p1 > self.p3:
            return 1
        elif self.p2 > self.p1 and self.p2 > self.p3:
            return 2
        elif self.p3 > self.p1 and self.p3 > self.p2:
            return 3

    def choice_maker_fixed(self):
        if self.p1 + self.p2 > self.p3:
            return [1,2]
        elif self.p2 + self.p3 > self.p1:
            return [2,3]
        elif self.p1 + self.p3 > self.p2:
            return [1,3]


def count_100_double_choice():
    app = Search("Cape Python")
    sailor_x, sailor_y = app.sailor_final_location(num_search_areas=3)
    search_num = 1

    while True:
        app.calc_search_effectiveness()

        if app.choice_maker_double() == 1:
            results_1, coords_1 = app.conduct_search(1, app.sa1, app.sep1)
            results_2, coords_2 = app.conduct_search(1, app.sa1, app.sep1)
            app.sep1 = (len(set(coords_1 + coords_2)) / (len(app.sa1) ** 2))
            app.sep2 = 0
            app.sep3 = 0
        elif app.choice_maker_double() == 2:
            results_1, coords_1 = app.conduct_search(2, app.sa2, app.sep2)
            results_2, coords_2 = app.conduct_search(2, app.sa2, app.sep2)
            app.sep1 = 0
            app.sep2 = (len(set(coords_1 + coords_2)) / (len(app.sa2) ** 2))
            app.sep3 = 0
        elif app.choice_maker_double() == 3:
            results_1, coords_1 = app.conduct_search(3, app.sa3, app.sep3)
            results_2, coords_2 = app.conduct_search(3, app.sa3, app.sep3)
            app.sep1 = 0
            app.sep2 = 0
            app.sep3 = (len(set(coords_1 + coords_2)) / (len(app.sa3) ** 2))

        app.revise_target_probe()
        if results_1 == "Nie znaleziono." and results_2 == "Nie znaleziono.":
            pass
        else:
            found_double.append(search_num)
            count_100_double_choice()
        if len(found_double) >= 100:
            break
        search_num += 1
    avg_local = sum(found_double) / len(found_double)
    return avg_local


def count_100_fixed_choice():
    app1 = Search("Cape Python")
    sailor_x, sailor_y = app1.sailor_final_location(num_search_areas=3)
    search_num = 1

    while True:
        app1.calc_search_effectiveness()

        if app1.choice_maker_fixed() == [1,2]:
            results_1_, coords_1 = app1.conduct_search(1, app1.sa1, app1.sep1)
            results_2_, coords_2 = app1.conduct_search(2, app1.sa2, app1.sep2)
            app1.sep3 = 0
        elif app1.choice_maker_fixed() == [2,3]:
            results_1_, coords_1 = app1.conduct_search(2, app1.sa2, app1.sep2)
            results_2_, coords_2 = app1.conduct_search(3, app1.sa3, app1.sep3)
            app1.sep1 = 0
        elif app1.choice_maker_fixed() == [1,3]:
            results_1_, coords_1 = app1.conduct_search(1, app1.sa1, app1.sep1)
            results_2_, coords_2 = app1.conduct_search(3, app1.sa3, app1.sep3)
            app1.sep2 = 0

        app1.revise_target_probe()

        if results_1_ == "Nie znaleziono." and results_2_ == "Nie znaleziono.":
            pass
        else:
            found_fixed.append(search_num)
            count_100_fixed_choice()
        if len(found_fixed) >= 100:
            break
        search_num += 1
    avg_local = sum(found_fixed) / len(found_fixed)
    return avg_local


def main():
    i = 0
    sum_major_double = 0
    sum_major_fixed = 0
    iterations = 100
    while i < iterations:
        count_100_double_choice()
        count_100_fixed_choice()
        iteration_avg_double = count_100_double_choice()
        iteration_avg_fixed = count_100_fixed_choice()
        sum_major_double += iteration_avg_double
        sum_major_fixed += iteration_avg_fixed
        i += 1
    avg_major_double = sum_major_double / iterations
    avg_major_fixed = sum_major_fixed / iterations
    print(f"Średnia ilość poszukiwań podwójnych dla {100*iterations} znalezień to: {avg_major_double}")
    print(f"Średnia ilość poszukiwań łączonnych dla {100*iterations} znalezień to: {avg_major_fixed}")


if __name__ == "__main__":
    main()