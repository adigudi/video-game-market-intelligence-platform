// clustering.cpp
// Build: from repo root -> cd cpp && g++ -std=c++17 clustering.cpp -o cluster_engine && cd ..
// (On Windows with MinGW/WSL, same command; ensure a C++17 compiler is available.)

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

struct Point {
    int game_id{};
    std::vector<double> features;
    int cluster{-1};
};

using Matrix = std::vector<std::vector<double>>;

std::vector<std::string> split(const std::string& line, char delim) {
    std::vector<std::string> parts;
    std::stringstream ss(line);
    std::string item;
    while (std::getline(ss, item, delim)) {
        parts.push_back(item);
    }
    return parts;
}

std::filesystem::path resolve_data_path(const std::string& filename) {
    // Prefer a nearby data/ directory, even if the file does not yet exist.
    std::filesystem::path cwd = std::filesystem::current_path();
    std::vector<std::filesystem::path> bases = {cwd, cwd.parent_path()};
    for (const auto& base : bases) {
        auto dir = base / "data";
        if (std::filesystem::exists(dir) && std::filesystem::is_directory(dir)) {
            return dir / filename;
        }
    }
    return cwd / "data" / filename;
}

std::vector<Point> read_csv(const std::filesystem::path& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open file: " + path.string());
    }

    std::vector<Point> points;
    std::string line;

    // Header
    if (!std::getline(file, line)) {
        throw std::runtime_error("Empty CSV: " + path.string());
    }

    while (std::getline(file, line)) {
        if (line.empty()) continue;
        auto parts = split(line, ',');
        if (parts.size() < 2) continue;
        Point p;
        p.game_id = std::stoi(parts[0]);
        p.features.reserve(parts.size() - 1);
        for (size_t i = 1; i < parts.size(); ++i) {
            p.features.push_back(std::stod(parts[i]));
        }
        points.push_back(std::move(p));
    }

    return points;
}

double euclidean_sq(const std::vector<double>& a, const std::vector<double>& b) {
    double sum = 0.0;
    for (size_t i = 0; i < a.size(); ++i) {
        double d = a[i] - b[i];
        sum += d * d;
    }
    return sum;
}

Matrix initialize_centroids(const std::vector<Point>& points, int k) {
    Matrix centroids;
    centroids.reserve(k);
    for (int i = 0; i < k; ++i) {
        // Deterministic init: first k points (assumes k <= points.size()).
        centroids.push_back(points[static_cast<size_t>(i % points.size())].features);
    }
    return centroids;
}

void assign_clusters(std::vector<Point>& points, const Matrix& centroids) {
    for (auto& p : points) {
        double best_dist = std::numeric_limits<double>::max();
        int best_cluster = -1;
        for (size_t i = 0; i < centroids.size(); ++i) {
            double d = euclidean_sq(p.features, centroids[i]);
            if (d < best_dist) {
                best_dist = d;
                best_cluster = static_cast<int>(i);
            }
        }
        p.cluster = best_cluster;
    }
}

Matrix update_centroids(const std::vector<Point>& points, int k, size_t dim) {
    Matrix centroids(k, std::vector<double>(dim, 0.0));
    std::vector<int> counts(k, 0);
    for (const auto& p : points) {
        if (p.cluster < 0) continue;
        for (size_t j = 0; j < dim; ++j) {
            centroids[p.cluster][j] += p.features[j];
        }
        counts[p.cluster] += 1;
    }
    for (int i = 0; i < k; ++i) {
        if (counts[i] == 0) continue;
        for (size_t j = 0; j < dim; ++j) {
            centroids[i][j] /= static_cast<double>(counts[i]);
        }
    }
    return centroids;
}

void write_clusters(const std::vector<Point>& points, const std::filesystem::path& path) {
    std::ofstream out(path);
    if (!out.is_open()) {
        throw std::runtime_error("Failed to write: " + path.string());
    }
    out << "game_id,cluster_id\n";
    for (const auto& p : points) {
        out << p.game_id << "," << p.cluster << "\n";
    }
}

int main(int argc, char* argv[]) {
    int k = 5;
    if (argc > 1) {
        k = std::stoi(argv[1]);
        if (k <= 0) {
            std::cerr << "k must be positive\n";
            return 1;
        }
    }
    const int iterations = 20;

    std::filesystem::path features_path = resolve_data_path("features_for_clustering.csv");
    if (!std::filesystem::exists(features_path)) {
        std::cerr << "Could not find features CSV at " << features_path << "\n";
        return 1;
    }

    auto points = read_csv(features_path);
    if (points.empty()) {
        std::cerr << "No data points found.\n";
        return 1;
    }
    size_t dim = points.front().features.size();

    auto centroids = initialize_centroids(points, k);

    for (int iter = 0; iter < iterations; ++iter) {
        assign_clusters(points, centroids);
        centroids = update_centroids(points, k, dim);
    }

    std::filesystem::path output_path = resolve_data_path("cluster_output.csv");
    write_clusters(points, output_path);

    std::cout << "Points: " << points.size() << "\n";
    std::cout << "Features per point: " << dim << "\n";
    std::cout << "Clusters: " << k << "\n";
    std::cout << "Iterations: " << iterations << "\n";
    std::cout << "Wrote clusters to: " << output_path << "\n";

    return 0;
}
