import pandas as pd
import math
from time import sleep

movie_rating_all = pd.read_csv("./movie.csv")
similarity_table_all = pd.read_csv("./sim.csv")
user_ids_all = movie_rating_all.columns[1:]

# * ---------------- BEGINNING OF CALCULATION SECTION ------------ * #

'''
calculate_sum_for_single_user
* returns   : multiplication between (similarity of user a and u) x (rating user u towards item i)
* param     : sau -> similarity value between a and u
              rui -> rating user u towards item i
'''


def calculate_sum_for_single_user(sau, rui):
    if not math.isnan(rui):
        result = rui * sau
        return result
    else:
        return 0


'''
calculate_sum_for_single_movie
* returns   : the sum value for each similar user to a multiplied by each user's similarity value
* param     : i -> item or movie index
              sim_table -> similarity values for neighboring users
              movie_table -> movie rating tables for neighboring users
              neighbor_users -> 10 most similar user to a
'''


def calculate_sum_for_single_movie(i, sim_table, movie_table, neighbor_users):
    result = 0
    for u in neighbor_users:
        # * r(u,i) : rating from user u towards movie i
        rating_u_i = movie_table[u][i]
        if math.isnan(rating_u_i):
            continue

        # u_index : index for user u
        u_index = sim_table[sim_table['userId'] == int(u)].index[0]
        # * s(a, u) : similarity between user a and user u
        sim = sim_table['sim'][u_index]

        result += calculate_sum_for_single_user(sau=sim, rui=rating_u_i)
    return result


'''
prediction_for_each_movie
* returns   : prediction dataframe for each movie that will be rated by each user
* param     : a -> the user which the prediction will be calculated
              sim_table -> similarity values for neighboring users to a
              movie_table -> movie rating tables for neighboring users to a
              neighbor_users -> 10 most similar user to a
'''


def prediction_for_each_movie(a, sim_table, movie_table, neighbor_users):
    neighbor_users.pop(0)
    sanitized_movie_table = pd.DataFrame(movie_table, columns=neighbor_users)

    # * ra -> average user rating to all movies
    rating_avg = movie_table[a].mean()

    # * sigma s(a,u) : sum of similairties between user a and user u
    sum_of_similarity = sim_table['sim'].sum()

    data = []

    epoch = 1
    for i, movie in sanitized_movie_table.iterrows():
        sum_of_prediction_value = calculate_sum_for_single_movie(
            i=i,
            sim_table=sim_table,
            movie_table=movie_table,
            neighbor_users=neighbor_users
        )
        sum_of_prediction_value /= sum_of_similarity
        prediction_value = rating_avg + sum_of_prediction_value

        prediction_value = min(prediction_value, 5.0)
        prediction_value = max(prediction_value, 0.0)
        data.append([i+1, prediction_value])

        if(epoch % 2000 == 0):
            print("Finished calculating for % d movies" % (epoch))
        epoch += 1

    return pd.DataFrame(data, columns=['movieId', 'rating prediksi'])


# * ---------------- END OF CALCULATION SECTION ----------------- * #


# * ---------------- BEGINNING OF UTILITY SECTION --------------- * #

def get_nearest_k_users_from_user_u(k, u):
    result = similarity_table_all.nlargest(
        k, u)
    result = result[[
        'userId', u]]
    result.rename(columns={
        u: 'sim'
    }, inplace=True)
    return result


# * ---------------- END OF UTILITY SECTION --------------------- * #


# * ---------------- BEGINNING OF UNIT TEST SECTION -------------- * #
# * To run unit test, simply call the run_unit_test in the main function
movie_rating_sample1 = pd.read_csv("./movie_sample1.csv")
similarity_table_sample1 = pd.read_csv("./sim_sample1.csv")
user_ids_sample1 = list(map(str, similarity_table_sample1['userId']))


def single_user_sample1():
    similarity_table_for_neighbor_users = similarity_table_sample1
    movie_table_for_neighbor_users = movie_rating_sample1
    result = []
    for user_id in user_ids_sample1:
        neighbor_users = user_ids_sample1
        result.append(prediction_for_each_movie(
            a=user_id,
            sim_table=similarity_table_for_neighbor_users,
            movie_table=movie_table_for_neighbor_users,
            neighbor_users=neighbor_users
        ))
        break

    print(result[0])


movie_rating_sample2 = pd.read_csv("./movie_sample2.csv")
similarity_table_sample2 = pd.read_csv("./sim_sample2.csv")
user_ids_sample2 = list(map(str, similarity_table_sample2['userId']))


def single_user_sample2():
    similarity_table_for_neighbor_users = similarity_table_sample2
    movie_table_for_neighbor_users = movie_rating_sample2
    result = []
    for user_id in user_ids_sample2:
        neighbor_users = user_ids_sample2
        result.append(prediction_for_each_movie(
            a=user_id,
            sim_table=similarity_table_for_neighbor_users,
            movie_table=movie_table_for_neighbor_users,
            neighbor_users=neighbor_users
        ))
        break

    print(result[0])


def run_unit_tests():
    single_user_sample1()
    single_user_sample2()

# * ---------------- END OF UNIT TEST SECTION ------------------- * #


# * ---------------- MAIN SECTION ------------------------------- * #
def main():
    for user_id in user_ids_all:
        similarity_table = get_nearest_k_users_from_user_u(11, user_id)
        neighbor_users = list(map(str, similarity_table['userId'].tolist()))
        movie_table = movie_rating_all[['movieId'] + neighbor_users]

        print("Calculating prediction for each movie for user id : ", user_id, " ... ")
        print(prediction_for_each_movie(
            a=user_id,
            sim_table=similarity_table,
            movie_table=movie_table,
            neighbor_users=neighbor_users
        ))


# * ---------------- END OF MAIN SECTION ----------------------- * #


if __name__ == "__main__":
    main()
