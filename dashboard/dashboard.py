import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

# Fungsi medapatkan kelompok data berdasarkan 'dteday' dan 'yr' dan menjumlahkan kolom 'cnt'
def create_grouped_df(df):
    df_grouped = df.groupby(['dteday', 'yr'])['cnt'].sum().unstack(fill_value=0)

    return df_grouped

# Fungsi mendapatkan data pola penyewaan by weorkingday
def create_byworkingday_df(df):
    byworkingday_df = df.groupby(by="workingday").agg({
        "dteday" : "nunique",
        "cnt" : ["sum", "min", "max", "mean", "std"]
    }).sort_values(by=("cnt", "sum"), ascending=False)

    return byworkingday_df

# Fungsi mendapatkan data pola penyewaan sepeda berdasarkan musimyang sedang terjadi
def create_byseason_df(df):
    byseason_df = df.groupby(by="season").agg({
        "dteday" : "nunique",
        "cnt" : ["sum", "min", "max", "mean"]
    }).sort_values(by=("cnt", "sum"), ascending=False) 

    return byseason_df

# Fungsi mendapatkan data pola penyewaan sepeda berdasarkan cuaca yang terjadi
def create_byweather_df(df):
    byweather_df = df.groupby(by="weathersit").agg({
        "dteday" : "nunique",
        "cnt" : ["sum", "min", 'max', "mean"]
    }).sort_values(by=("cnt", "sum"), ascending=False)

    return byweather_df

# Fungsi mendapatkan data tren penyewaan antara casual user dan registered user perbulan
def create_type_user_month_df(df):
    type_user_month_df = df.groupby(by="mnth").agg({
        "mnth" : "nunique",
        "casual" : "sum",
        "registered" : "sum",
        "cnt" : "sum"
    })

    return type_user_month_df

# Fungsi mendapatkan data pola penyewaan sepeda berdasarkan jam
def create_byhour_df(df):
    byhour_df = df.groupby(by="hr").agg({
        "hr" : "nunique",
        "cnt" : ["sum", "min", "max", "mean"]
    }).sort_values(by=("cnt", "sum"), ascending=False)
    return byhour_df

# Fungsi medapatkan pengaruh kondisi cuaca seperti `temp`, `hum`, dan `windspeed` menggunakan correlation matrix
def create_correlation_matrix(df):
    correlation_matrix = df[["temp", "hum", "windspeed", "cnt"]].corr()
    
    return correlation_matrix

# Fungsi mendapatkan data jumlah pengguna casual dan registered berdasarkan jam (hr) dan workingday
def create_casual_user_hour_df(df):
    casual_users = df[df['workingday'] == 0].groupby('hr')['casual'].sum()

    return casual_users

def create_registered_user_hour_df(df):   
    registered_users = df[df['workingday'] == 1].groupby('hr')['registered'].sum()

    return registered_users

# Fungsi mendapatkan data rfm analysis
def create_rfm_df(df):
    rfm_df = df.groupby("weekday_name").agg({
        "dteday": lambda x: (df["dteday"].max() - x.max()).days,  # Recency
        "cnt": ["count", "sum"]  # Frequency and Monetary
    }).reset_index()

    # Rename columns
    rfm_df.columns = ["weekday", "recency", "frequency", "monetary"]

    # Sort by weekday
    weekday_order = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    rfm_df["weekday"] = pd.Categorical(rfm_df["weekday"], categories=weekday_order, ordered=True)
    rfm_df.sort_values(by="weekday", inplace=True)

    return rfm_df

# Load cleaned data
day_df = pd.read_csv('https://raw.githubusercontent.com/Prayoga-bit/Bike-Sharing-Data-Analysis/refs/heads/main/dashboard/day_clean.csv')
hour_df = pd.read_csv('https://raw.githubusercontent.com/Prayoga-bit/Bike-Sharing-Data-Analysis/refs/heads/main/dashboard/hour_clean.csv')

# Memastikan dteday dalam bentuk datetime
day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(day_df["dteday"])

# Filter data
min_date = min(hour_df["dteday"].min(), day_df["dteday"].min()).date()
max_date = max(hour_df["dteday"].max(), day_df["dteday"].max()).date()

try:
    with st.sidebar:
        # Set logo
        st.image("https://rb.gy/faknv0", output_format='PNG', width= 300)

        # Mengambil start_date & end date dari input
        start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date])
    
    main_df_days = day_df[(day_df["dteday"] >= str(start_date)) & 
                        (day_df["dteday"] <= str(end_date))]

    main_df_hours = hour_df[(hour_df["dteday"] >= str(start_date)) & 
                            (hour_df["dteday"] <= str(end_date))]

    # st.dataFrame(main_df)
    grouped_df = create_grouped_df(main_df_days)
    byworkingday_df = create_byworkingday_df(main_df_days)
    byseason_df = create_byseason_df(main_df_days)
    byweather_df = create_byweather_df(main_df_days)
    type_user_month_df = create_type_user_month_df(main_df_days)
    byhour_df = create_byhour_df(main_df_hours)
    correlation_matrix = create_correlation_matrix(main_df_hours)
    casual_user = create_casual_user_hour_df(main_df_hours)
    registered_user = create_registered_user_hour_df(main_df_hours)
    rfm_df = create_rfm_df(main_df_days)

    # plot number of daily orders (2021)
    st.header('Bike Sharing Dashboard :sparkles:')
    st.subheader('Bike Sharing Productivity')

    col1, col2 = st.columns(2)

    with col1:
        total_sewa_registered = main_df_days.registered.sum()
        st.metric("Registered user", value=total_sewa_registered)

    with col2:
        total_sewa = main_df_days.cnt.sum()
        st.metric("Total Penyewaan", value=total_sewa)

    # Membuat figure untuk grafik
    plt.figure(figsize=(15, 6))

    for year in grouped_df.columns:
        plt.plot(grouped_df.index, grouped_df[year], label=f"Year {year}", marker='o', linestyle='-')

    # Menambahkan judul, label, legend, dan grid
    plt.title("Yearly Total Users per Day", loc="center", fontsize=20)
    plt.ylabel("Total Users", fontsize=12)
    plt.xticks(rotation=45)  # Rotasi label tanggal
    plt.legend(fontsize=12)
    plt.grid(True)

    # Menampilkan grafik dengan Streamlit
    st.pyplot(plt)

    # Explanation
    with st.expander("Explantion"):
        st.write("""Penyewaan overall mengalami peningkatan dari tahun 2011 ke 2012, namun pada 2012 akhir penyewaan menalami penurunan walaupun pola ini serupa pada tahun sebelumnya namun harus menjadi perhatian agar bisa membuat strategi untuk meniningkatkan penyewaan sepeda pada akhir tahun""")

    st.subheader("Bike Sharing Pattern by Time")
    tab1, tab2 = st.tabs(["Season", "Hourly"])

    with tab1:
        # Membuat figure untuk grafik
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 6))

        # Grafik berdasarkan musim
        colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
        byseason_df[('cnt', 'sum')].plot(kind='bar', ax=ax1, color=colors)
        ax1.set_title('Total Rentals by Season', fontsize=12, pad=15)
        ax1.set_xlabel(None)
        ax1.set_ylabel(None)
        ax1.tick_params(axis='x', rotation=45)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

        # menambahkan nilai rata-rata sebagau garis
        ax1_twin = ax1.twinx()
        byseason_df[('cnt', 'mean')].plot(color='red', marker='o', linestyle='-', ax=ax1_twin)
        ax1_twin.set_ylabel('Mean Rentals', color='red')
        ax1_twin.tick_params(axis='y', labelcolor='red')

        # Grafik berdasarkan cuaca
        byweather_df[('cnt', 'sum')].plot(kind='bar', ax=ax2, color=colors)
        ax2.set_title('Total Rentals by Weather', fontsize=12, pad=15)
        ax2.set_xlabel(None)
        ax2.set_ylabel(None)
        ax2.tick_params(axis='x', rotation=45)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

        # menambahkan nilai rata-rata sebagau garis
        ax2_twin = ax2.twinx()
        byweather_df[('cnt', 'mean')].plot(color='red', marker='o', linestyle='-', ax=ax2_twin)
        ax2_twin.set_ylabel('Mean Rentals', color='red')
        ax2_twin.tick_params(axis='y', labelcolor='red')

        # Grafik berdasarkan workingday
        byworkingday_df[('cnt', 'sum')].plot(kind='bar', ax=ax3, color=colors)
        ax3.set_title('Total Rentals by Day Type', fontsize=12, pad=15)
        ax3.set_xlabel(None)
        ax3.set_ylabel(None)
        ax3.tick_params(axis='x', rotation=45)
        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

        # menambahkan nilai rata-rata sebagau garis
        ax3_twin = ax3.twinx()
        byworkingday_df[('cnt', 'mean')].plot(color='red', marker='o', linestyle='-', ax=ax3_twin)
        ax3_twin.set_ylabel('Mean Rentals', color='red')
        ax3_twin.tick_params(axis='y', labelcolor='red')

        # Menambahkan Title
        plt.suptitle("Bike Sharing By Time", fontsize=20)

        # Show the plot with streamlit
        st.pyplot(plt)

    with tab2:
        # Membuat figure untuk grafik
        fig, ax = plt.subplots(figsize=(20,6))

        # Plot data pengguna by hour
        sns.pointplot(data=hour_df, x="hr", y="cnt", errorbar=None, ax=ax)

        # Menambahkan judul, label sumbu, dan legend
        ax.set_title('Total Rentals per Hour', fontsize=16, pad=15)
        ax.set_xlabel("Hour of the Day")
        ax.set_ylabel("Number of Users")

        # Menampilkan grafik
        plt.tight_layout()
        st.pyplot(plt)

    with st.expander("Explanation"):
        st.write("Pola penyewaan tertinggi terjadi ketika musim fall dan saat cuaca sedang cerah dan mendukung untuk bersepeda karena saat hujan ringan tidak ada data penyewaan, sedangkan waktu terbanyak penyewaan adalah saat hari kerja dengan jam 8 bisa diasumsikan berangkat dan 17-18 bisa diasumsikan saat pulang aktivitas. Dengan adanya pola ini maka dapat memperluas penyewaan terhadap tempat-tempat yang berlokasi sekitar perusahaan ataupun sekolah dan kampus.")

    st.subheader("Bike Sharing Correlation Of Weather")
    # Membuat figure untuk grafik
    fig, ax = plt.subplots(figsize=(10,6))

    # Menampilkan grafikdari correlation-matric
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
    plt.title('Correlation Matrix')

    # Menampilkan Grafik
    st.pyplot(fig)

    with st.expander("Explanation"):
        st.write("parameter yang berpengaruh positif terhadap jumlah penyewaan sepeda adalah temperature, sedangkan humidity berkorelasi negatif yang artinya customerakan melakukan penyewaan sepeda ketika suhu dan kelembapan ideal untuk bersepeda.")

    st.subheader("Bike Sharing Trends between Casual and Registered Users")

    tab1, tab2 = st.tabs(["Monthly", "Hourly"])

    with tab1:
        # Membuat figure grafik
        plt.figure(figsize=(14, 6))

        # Plot data untuk casual users
        plt.plot( type_user_month_df.index, type_user_month_df["casual"], label="Casual Users", color="blue", marker="o", linestyle="-")

        # Plot data untuk registered users
        plt.plot( type_user_month_df.index, type_user_month_df["registered"], label="Registered Users", color="green", marker="o", linestyle="-")

        # Menambahkan judul, label sumbu, dan legend
        plt.title("Monthly Comparison of Casual and Registered Users", fontsize=16, pad=20)
        plt.xlabel("Year (Month)", fontsize=12)
        plt.ylabel("Number of Users", fontsize=12)
        plt.legend(fontsize=12, loc='upper left')
        plt.grid(True, linestyle='--', alpha=0.7)

        # menampilkan grafik
        st.pyplot(plt)

    with tab2:
        # Membuat figure untuk grafik
        plt.figure(figsize=(14, 6))

        # Plot data pengguna casual (workday)
        plt.plot(casual_user.index, casual_user.values, label="Casual Users (Workday)", color="blue", marker="o", linestyle="-")

        # Plot data pengguna registered (weekend)
        plt.plot(registered_user.index, registered_user.values, label="Registered Users (Weekend)", color="green", marker="o", linestyle="-")

        # Menambahkan judul, label sumbu, dan legend
        plt.title("Hourly Comparison of Casual and Registered Users", fontsize=16)
        plt.xlabel("Hour of the Day", fontsize=12)
        plt.ylabel("Number of Users", fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True)

        # Menampilkan grafik
        st.pyplot(plt)

    with st.expander("Explanation"):
        st.write("Untuk monthly pola peningkatan antara casual user dan registered user hampir memiliki pola yang sama, namun ada perbedaan sedikit pada bulan 7 ketika casual user mengalami peningkatan disisi lain registered user mengalami penurunan, kemudian untuk pola hourly registered user memiliki pola peningkatan yang tinggi pada pagi hari dan sore hari.")

    st.subheader("Bike Sharing RFM Analysis")

    # membuat fig grafik
    fig, ax = plt.subplots(1, 3, figsize=(18, 6), sharey=False)

    # Color palette
    colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

    # Recency Plot
    ax[0].bar(rfm_df["weekday"], rfm_df["recency"], color=colors)
    ax[0].set_title("Recency by Weekday")
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)

    # Frequency Plot
    ax[1].bar(rfm_df["weekday"], rfm_df["frequency"], color=colors)
    ax[1].set_title("Frequency by Weekday")
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)

    # Monetary Plot
    ax[2].bar(rfm_df["weekday"], rfm_df["monetary"], color=colors)
    ax[2].set_title("Monetary by Weekday")
    ax[2].set_ylabel(None)
    ax[2].set_xlabel(None)
    plt.suptitle("Best Day Customer based RFM Analysis (weekday)", fontsize=20)

    # atur layout dan menampilkan grafik
    st.pyplot(plt)

    with st.expander("Explanation"):
        st.write("Recency terjadi pada hari selasa, sedangkan frequency memiliki pola yang hampir sama,dan monetary tertinggi pada Kamis dan Jumat")

    st.caption("Prayoga Agus Setiawan @2025")

except Exception as e:
    # Menampilkan pesan error saat memilih filter
    st.error("Pilih Rentang Waktu")
